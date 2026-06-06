## Why

El scaffold de C-01 dejó los directorios `models/`, `repositories/` y el slot `core/tenancy.py` vacíos. Sin el modelo `Tenant`, el mixin base de entidad ni el repositorio genérico con aislamiento por tenant, ningún modelo de dominio (alumnos, cursos, inscripciones) puede existir ni garantizar la separación de datos entre inquilinos. C-02 construye ese piso de dominio.

## What Changes

- **Modelo `Tenant`** como primera entidad del sistema, con campos de negocio (nombre, slug, configuración) y el mixin base de auditoría.
- **Mixin base `EntityMeta`** en `models/base.py` con `id` (UUID v7), `tenant_id`, `created_at`, `updated_at`, `deleted_at` (soft delete). Todas las entidades de dominio heredan de esta clase.
- **Repositorio genérico `BaseRepository[T]`** en `repositories/base.py` con operaciones CRUD estándar y **filtro automático por `tenant_id`** en cada query. Toda consulta sin tenant scope se considera bug.
- **Helper de encriptación AES-256-CBC** en `core/security.py` (slot reservado en C-01) para atributos PII (DNI, CUIL, CBU, email) con marcador `[cifrado]`.
- **Pipeline de excepciones de dominio** en `core/exceptions.py` (slot reservado en C-01): `TenantNotFoundError`, `EntityNotFoundError`, `EncryptionError`.
- **Alembic Migration 001**: crea la tabla `tenant`.
- **Dependencia `cryptography`** agregada a `pyproject.toml`.
- **Tests**: suite completa de aislamiento multi-tenant, soft-delete, encriptación round-trip y timestamps del mixin.

No hay cambios BREAKING — C-02 es aditivo sobre C-01.

## Capabilities

### New Capabilities

- `tenant-model`: Modelo `Tenant` raíz del sistema, con slug único, nombre, configuración JSON y timestamps de auditoría.
- `entity-mixin`: Mixin base `EntityMeta` con UUID v7, `tenant_id`, timestamps y soft-delete para todas las entidades de dominio.
- `repositorio-generico`: `BaseRepository[T]` con CRUD tipado, filtro automático por `tenant_id` y visibilidad explícita de borrados.
- `encryption-helper`: Encriptación AES-256-CBC para atributos PII — cifrado/descifrado con clave desde `Settings.ENCRYPTION_KEY`.
- `exception-pipeline`: Excepciones de dominio estandarizadas (`TenantNotFoundError`, `EntityNotFoundError`, `EncryptionError`).

### Modified Capabilities

<!-- Ninguna: es el primer change de dominio, no hay specs previos que modificar. -->

## Impact

- **Nuevo código**: `models/tenant.py`, `models/base.py`, `models/__init__.py` (updated), `repositories/base.py`, actualización de `core/security.py` y `core/exceptions.py`.
- **Migración**: `alembic/versions/001_create_tenant.py` — primera migración de dominio.
- **Dependencia nueva**: `cryptography` agregada a `pyproject.toml`.
- **Configuración**: `ENCRYPTION_KEY` ya existe en `Settings` (C-01) con validación de 32 bytes — queda operativa.
- **Tests**: `tests/test_tenant_model.py`, `tests/test_entity_mixin.py`, `tests/test_repository_base.py`, `tests/test_encryption.py`.
- **Habilita**: C-03 (auth), C-04 (RBAC) y todos los modelos de dominio futuros (alumno, curso, inscripción, etc.).
- **Governance**: CRÍTICO — cimiento de aislamiento multi-tenant. Una falla en el filtro de repositorio expone datos entre inquilinos.
