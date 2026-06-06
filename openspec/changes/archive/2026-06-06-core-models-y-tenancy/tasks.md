## 1. Dependencia y excepciones de dominio

- [x] 1.1 Agregar `cryptography>=42.0.0,<43.0.0` a `pyproject.toml` e instalar
- [x] 1.2 Implementar `core/exceptions.py` con `DomainError` base, `TenantNotFoundError`, `EntityNotFoundError`, `EncryptionError` — cada uno con `detail: str` y `context: dict`

## 2. EntityMeta mixin (models/base.py)

- [x] 2.1 (RED) Escribir `tests/test_entity_mixin.py`: verificar que una entidad concreta que hereda `EntityMeta` tiene columnas `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`
- [x] 2.2 (GREEN) Implementar `models/base.py` con `EntityMeta` como `__abstract__ = True`: `id` UUID pk default uuid4, `tenant_id` UUID FK a `tenant.id`, `created_at`/`updated_at` con timezone y server_default, `deleted_at` nullable
- [x] 2.3 (TRIANGULATE) Verificar que `updated_at` se actualiza al modificar y que `deleted_at` se puede setear explícitamente

## 3. Modelo Tenant (models/tenant.py)

- [x] 3.1 (RED) Escribir `tests/test_tenant_model.py`: crear tenant con slug único, verificar slug duplicado falla, verificar `config` default `{}`, verificar timestamps automáticos
- [x] 3.2 (GREEN) Implementar `models/tenant.py` con `Tenant(EntityMeta)`: `slug` (VARCHAR(100), UNIQUE, NOT NULL), `name` (VARCHAR(255), NOT NULL), `config` (JSONB, default `{}`)
- [x] 3.3 (TRIANGULATE) Verificar FK constraint: crear entidad con tenant_id inexistente falla; crear con tenant existente persiste

## 4. Helper de encriptación AES-256 (core/security.py)

- [x] 4.1 (RED) Escribir `tests/test_encryption.py`: round-trip encrypt → decrypt retorna mismo texto, output tiene prefijo `[cifrado]`, ciphertext distintos para mismo input (IV diferente), `is_encrypted` detecta formato, decrypt con input inválido lanza `EncryptionError`
- [x] 4.2 (GREEN) Implementar en `core/security.py`: `encrypt(plaintext: str) -> str`, `decrypt(ciphertext: str) -> str`, `is_encrypted(value: str) -> bool` usando AES-256-CBC con HKDF de `ENCRYPTION_KEY`
- [x] 4.3 (TRIANGULATE) Verificar que `ENCRYPTION_KEY` de 32 chars funcione correctamente y que error de decrypt no expone texto plano en mensaje

## 5. Repositorio genérico (repositories/base.py)

- [x] 5.1 (RED) Escribir `tests/test_repository_base.py`: instanciar `BaseRepository[T]` con tenant_id, `create` persiste con tenant_id correcto, `get` solo retorna entidad del mismo tenant y no borrada, `get_all` respeta tenant scope, `get_all(include_deleted=True)` incluye borrados, `update` falla si no es del tenant, `soft_delete` setea deleted_at, `count` cuenta solo activos del tenant
- [x] 5.2 (GREEN) Implementar `repositories/base.py` con `BaseRepository[T: EntityMeta]`: constructor recibe `model` y `tenant_id`, métodos `create`, `get`, `get_all`, `update`, `soft_delete`, `count` con filtro automático de tenant y soft-delete
- [x] 5.3 (TRIANGULATE) Verificar aislamiento multi-tenant real: crear entidades en tenant A y B, confirmar que tenant A no ve datos de tenant B ni viceversa

## 6. Migración Alembic 001

- [x] 6.1 Generar migración con `alembic revision --autogenerate -m "create_tenant"` y revisar que el upgrade crea la tabla `tenant` con todas las columnas y constraints
- [x] 6.2 Verificar que `alembic upgrade head` aplica sin error contra DB de test y que `alembic downgrade -1` dropea la tabla

## 7. Actualización de exports

- [x] 7.1 Actualizar `models/__init__.py` para exportar `EntityMeta` y `Tenant`
- [x] 7.2 Verificar que `Base` en `core/database.py` es compatible con declarative mixins (no requiere cambios, verificar import)

## 8. Verificación final

- [x] 8.1 Ejecutar `pytest` completo y confirmar verde: entity mixin, tenant model, encryption, repository, más tests existentes de C-01
- [x] 8.2 Confirmar que `cryptography` no rompe el build de Docker (builder compila, runtime usa wheels)
- [x] 8.3 Verificar que ningún archivo nuevo supera 500 LOC
