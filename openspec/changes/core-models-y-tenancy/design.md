## Context

C-01 dejó el scaffold del backend con `models/__init__.py`, `repositories/__init__.py` y los slots `core/tenancy.py` y `core/exceptions.py` como placeholders vacíos. El contrato de arquitectura (ADR-002) exige multi-tenancy row-level desde el día 0: cada tabla de dominio tiene `tenant_id`, cada query filtra por inquilino, y el borrado es siempre lógico.

Hoy no existe un solo modelo de dominio, repositorio, ni migración. C-02 (governance **CRÍTICO**) materializa el cimiento de entidades: Tenant como raíz, mixin base EntityMeta para todas las entidades futuras, repositorio genérico con tenant scope automático, helper de encriptación AES-256 para PII, y la primera migración de dominio.

## Goals / Non-Goals

**Goals:**

- Modelo `Tenant` con slug único, nombre, JSON de configuración y timestamps de auditoría.
- Mixin `EntityMeta` (declarative mixin de SQLAlchemy) que todas las entidades de dominio heredan: `id` UUID, `tenant_id` FK, `created_at`, `updated_at`, `deleted_at`.
- `BaseRepository[T]` genérico con CRUD completo: `create`, `get`, `get_all`, `update`, `soft_delete`, `count`. Cada método filtra automáticamente por `tenant_id` y excluye registros con `deleted_at IS NOT NULL`.
- Helper AES-256-CBC en `core/security.py` para cifrar/descifrar atributos PII con la `ENCRYPTION_KEY` de Settings.
- Excepciones de dominio estandarizadas en `core/exceptions.py`: `TenantNotFoundError`, `EntityNotFoundError`, `EncryptionError`.
- Migración Alembic 001 que crea la tabla `tenant`.
- Tests: aislamiento multi-tenant, soft-delete, encryption round-trip, timestamps de mixin.

**Non-Goals:**

- Auth, JWT, sesión de usuario (→ C-03).
- Resolución de tenant desde request (header/domain/subdomain) — C-03 completa `core/tenancy.py` con el middleware/dependency que extrae el tenant. C-02 crea el modelo y el repositorio, pero el tenant se inyecta como `uuid.UUID`.
- Modelos de dominio de negocio (alumno, curso, inscripción) — esos llegan en changes posteriores de Fase 1.
- RBAC ni permisos (→ C-04).
- Worker, colas ni integración con Moodle (changes de integración).

## Decisions

### D1 — UUID v4 como PK (postergar UUID v7 a Python 3.14)

El mixin usa `Column(Uuid, primary_key=True, default=uuid.uuid4)`. Python 3.13 aún no tiene `uuid.uuid7()` nativo (llega en 3.14). Implementar uuid7 manualmente o con una dependencia extra no justifica el beneficio incremental de time-ordering para el alcance actual. El diseño migrará a `uuid.uuid7()` sin breaking change cuando el proyecto avance a Python 3.14.

**Alternativa descartada**: implementar uuid7 manualmente o con `uuid6` — overengineering para un proyecto que arranca. La PK UUID con uuid4 cumple, y el hot path de inserción no es cuello de botella en Fase 1.

### D2 — EntityMeta como declarative mixin de SQLAlchemy

`EntityMeta` se implementa como una clase mixin de SQLAlchemy (`as_declarative=True` no es necesario: se declara como clase con `__abstract__ = True` y `declared_attr` para `tenant_id`). Esto permite que los modelos concretos hereden columnas y comportamiento sin repetir código.

```python
class EntityMeta:
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tenant.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
```

**Alternativa descartada**: usar `Base` directamente con las columnas — contaminaría la tabla auxiliar de Alembic y rompe la separación entre scaffolding (`Base` en database.py) y dominio.

### D3 — BaseRepository[T] con tenant scope como contrato

`BaseRepository[T: EntityMeta]` recibe `tenant_id` en el constructor y todas las operaciones lo aplican automáticamente. Una instancia sin `tenant_id` es inválida.

```python
class BaseRepository[T: EntityMeta]:
    def __init__(self, model: type[T], tenant_id: uuid.UUID) -> None: ...
```

Métodos expuestos:
- `create(session, data: dict) -> T`
- `get(session, id: uuid.UUID) -> T | None` — filtra por tenant_id + deleted_at
- `get_all(session, *, include_deleted: bool = False, **filters) -> Sequence[T]`
- `update(session, id: uuid.UUID, data: dict) -> T` — si no existe o no pertenece al tenant, raise EntityNotFoundError
- `soft_delete(session, id: uuid.UUID) -> None` — setea deleted_at, no DELETE físico
- `count(session, **filters) -> int`

Cada método construye la query base con `select(model).where(model.tenant_id == self._tenant_id, model.deleted_at.is_(None))`.

**Alternativa descartada**: aplicar el filtro vía event listener de SQLAlchemy o middleware de sesión. Son más difíciles de testear y depurar, y el filtro implícito viola el principio de sorpresa mínima. El filtro explícito en el repositorio es verificable, testeable y no depende de magia de sesión.

### D4 — AES-256-CBC con HKDF de ENCRYPTION_KEY

La `ENCRYPTION_KEY` (32 bytes, validada en Settings) se usa como material de entrada para HKDF con SHA-256, generando una key de 32 bytes y un IV determinista derivado del mismo material. Funciones:

- `encrypt(plaintext: str) -> str`: cifra con AES-256-CBC, retorna base64 con prefijo `[cifrado]`
- `decrypt(ciphertext: str) -> str`: recibe base64, descifra y retorna el texto plano
- `is_encrypted(value: str) -> bool`: detecta prefijo `[cifrado]`

Nunca se loguea el valor plano. Los schemas de salida pueden descifrar automáticamente para usuarios autorizados (control en C-04/RBAC).

**Alternativa descartada**: Fernet (cryptography.fernet). Añade overhead de HMAC que no necesitamos — los datos viajan por canales TLS y la integridad se maneja a nivel de aplicación. AES-256-CBC directo es suficiente, más simple de debuggear y sin dependencia extra.

### D5 — Excepciones de dominio con contexto estructurado

Todas heredan de `DomainError(Exception)` que lleva `detail: str` y `context: dict`:

- `TenantNotFoundError(tenant_id)` → 404 con `{"detail": "Tenant not found", "context": {"tenant_id": ...}}`
- `EntityNotFoundError(entity_type, entity_id)` → 404 con `{"detail": "... not found"}`
- `EncryptionError(message)` → 500 (fallo de infraestructura, no se expone el detalle al cliente)

Los handlers de FastAPI capturan `DomainError` y devuelven JSON con status code según la subclase.

### D6 — Migración Alembic 001 declarativa

Se genera con `alembic revision --autogenerate -m "create_tenant"`. La migración crea la tabla `tenant` con columnas: `id` (UUID, PK, default gen_random_uuid()), `slug` (VARCHAR(100), UNIQUE, NOT NULL), `name` (VARCHAR(255), NOT NULL), `config` (JSONB, default '{}'), `created_at`, `updated_at`, `deleted_at`.

El downgrade dropea la tabla.

## Risks / Trade-offs

- **[UUID v4 vs v7: performance en inserts masivos]** → Mitigación: aceptado para Fase 1. Si en el futuro hay inserts batch que degraden por fragmentación de índice, migrar a uuid7 no es breaking.
- **[Tenant filter en repositorio no cubre queries ad-hoc en services]** → Mitigación: los services deben recibir tenant_id y pasarle al repositorio. El contrato del repositorio lo fuerza. Si un service construye queries con la sesión directamente, es bug.
- **[ENCRYPTION_KEY rotación requiere re-cifrar datos existentes]** → Mitigación: este change no implementa rotación. En C-03 (o un change dedicado) se agrega key versioning con prefijo de versión en el ciphertext, permitiendo re-cifrado lazy al leer.
- **[AES-256-CBC no autentica el ciphertext]** → Mitigación: la integridad está cubierta por TLS en tránsito y el control de acceso a la DB en reposo. Si se requiere authenticated encryption en el futuro, migrar a AES-GCM es compatible.
- **[cryptography es una dependencia nativa con bindings C]** → Mitigación: ya es la librería estándar de facto para crypto en Python. El Dockerfile multi-stage la maneja sin problema (builder compila, runtime copia el wheel).

## Migration Plan

1. Agregar `cryptography` a `pyproject.toml` e instalar.
2. Implementar `core/exceptions.py` con `DomainError` + subclases.
3. Implementar `models/base.py` con `EntityMeta` mixin.
4. Implementar `models/tenant.py` con `Tenant`.
5. Implementar `repositories/base.py` con `BaseRepository[T]`.
6. Implementar helper AES-256 en `core/security.py`.
7. Actualizar `models/__init__.py` para exportar `EntityMeta`, `Tenant`.
8. Generar migración Alembic 001 con `--autogenerate` y revisarla.
9. Escribir tests en TDD: modelo, mixin, repositorio, encriptación.
10. Verificar suite completa verde.

Rollback: `alembic downgrade -1` dropea la tabla tenant. Las demás son solo adiciones de código sin efectos laterales.

## Open Questions

- **¿Cómo se resuelve el tenant_id en los tests?** Opciones: (a) crear un `Tenant` en fixture con `async_session` y usarlo, (b) pasar un `uuid.UUID` falso. Recomendación: (a) — los tests de repositorio deben probar aislamiento real, y un tenant falso no replica el FK constraint.
- **¿Esquema de nombres de tabla?** Se usa snake_case plural (`tenants`, `alumnos`, etc.) vs singular (`tenant`, `alumno`). Recomendación: plural, consistente con convención SQLAlchemy default (no especificar `__tablename__` lo genera automáticamente como snake_case plural).
