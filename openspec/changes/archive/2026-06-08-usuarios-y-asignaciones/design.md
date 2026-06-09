## Context

El proyecto ya cuenta con:
- `models/user.py`: modelo básico con email, hashed_password, totp_secret, is_active + roles relationship.
- `core/security.py`: AES-256-CBC encrypt/decrypt con prefijo `[cifrado]` y tests de round-trip.
- `repositories/base.py`: `BaseRepository[T]` con tenant scope automático (`_base_query()` filtra por `tenant_id` y `deleted_at IS NULL`).
- `models/base.py`: `EntityMeta` mixin con `id` (UUID), `tenant_id`, `created_at`, `updated_at`, `deleted_at`.
- `core/exceptions.py`: `EntityNotFoundError`, `EncryptionError`, `DomainError`.

No existe aún:
- `routers/` directory (los routers actuales están probablemente en `main.py` o sueltos).
- `crypto.py` separado (todo vive en `security.py`).
- Modelo `Asignacion` ni repositorio/service asociado.

## Goals / Non-Goals

**Goals:**
- Agregar los campos de identidad PII al modelo `User` existente (no reemplazarlo).
- Crear el modelo `Asignacion` como entidad separada (no mezclar con `UserRol`).
- ABM de usuarios con PII cifrada automáticamente en la capa de servicio.
- CRUD de asignaciones con validación de vigencia.
- Unicidad `(tenant_id, email)` — ya existe, se mantiene.
- Migración Alembic que altera la tabla `users` y crea `asignacion`.
- Tests de aislamiento multi-tenant, PII no expuesta, vigencia.

**Non-Goals:**
- No se modifican permisos existentes (C-04 ya implementó RBAC).
- No se implementan aún las vistas "mis equipos", clonado, ni asignación masiva (eso es C-08).
- No se toca el flujo de autenticación (C-03).
- No se implementa cifrado de búsqueda por email (se usa el campo hash existente o búsqueda directa — el modelo actual no tiene hash de búsqueda).

## Decisions

### D1: Extender User existente vs crear modelo separado
- **Decisión**: Extender `models/user.py` con los nuevos campos.
- **Alternativa considerada**: Crear `UserProfile` con relación 1:1.
- **Razón**: El modelo actual es minimalista pero ya es la identidad del usuario. Agregar campos directamente evita joins innecesarios y simplifica las queries. La separación de concerns (auth vs perfil) se maneja a nivel de schemas/services, no de tablas.

### D2: Asignacion como modelo independiente, no como extensión de UserRol
- **Decisión**: Crear `models/asignacion.py` con todos los campos del dominio.
- **Alternativa considerada**: Extender `UserRol` con contexto académico.
- **Razón**: `UserRol` es una tabla junction simple para auth (C-04). `Asignacion` tiene semántica de dominio: vigencia, jerarquía, contexto académico. Mezclarlas crearía acoplamiento entre RBAC y gestión de equipos.

### D3: Cifrado PII en el service layer, no en el modelo
- **Decisión**: El `UsuarioService` llama a `encrypt()`/`decrypt()` explícitamente antes de persistir/devolver datos.
- **Alternativa considerada**: Usar un type decorator de SQLAlchemy o `@validates` en el modelo.
- **Razón**: El cifrado es una preocupación de seguridad, no de mapeo ORM. Mantenerlo en el service layer hace que sea explícito y testeable. Los `@validates` de SQLAlchemy pueden tener side effects difíciles de rastrear.

### D4: `estado_vigencia` como campo derivado, no almacenado
- **Decisión**: `Asignacion.estado_vigencia` es una property calculada a partir de `desde`/`hasta`.
- **Alternativa considerada**: Almacenarlo como columna y actualizarlo con un job.
- **Razón**: Es un valor puramente derivado. Almacenarlo introduciría riesgo de inconsistencia.

### D5: RBAC usa permisos existentes de C-04
- **Decisión**: Los endpoints nuevos usan `require_permission("usuarios:gestionar")` y `require_permission("equipos:asignar")`.
- **Razón**: Ya existe el sistema de permisos finos. Los guards se declaran en los routers y se validan contra la matriz de C-04.

## Risks / Trade-offs

- **[Riesgo] Modificar la tabla `users` puede afectar sesiones existentes**: los campos nuevos tienen defaults o son nullable, por lo que la migración es compatible hacia atrás. → **Mitigación**: migración con `ALTER TABLE ADD COLUMN ...` con valores por defecto.
- **[Riesgo] El cifrado en service layer puede omitirse por error**: si un desarrollador nuevo usa `BaseRepository` directamente sin pasar por el service. → **Mitigación**: el repositorio de usuario hereda de `BaseRepository` y el service es la única vía de acceso desde los routers. Los tests verifican que los datos cifrados no aparezcan en texto plano en la DB.
- **[Trade-off] Sin test de búsqueda por email en PII**: el modelo actual no tiene un campo `email_hash` para búsqueda determinística. La unicidad `(tenant_id, email)` existe a nivel DB sobre el campo cifrado, pero buscar por email requeriría descifrar en memoria. → Se acepta para este change; se puede agregar un campo hash en C-09 o C-08 si es necesario.
