## Why

El modelo `User` actual solo tiene los campos mínimos para autenticación (email, password, TOTP). No contiene los datos de identidad del docente —nombre, DNI, CUIL, CBU, etc.— que son necesarios para liquidaciones, reportes y gestión institucional. Tampoco existe el concepto de **Asignacion** que vincula a un usuario con un rol y un contexto académico (materia, carrera, cohorte), necesario para que los módulos posteriores (equipos docentes, padrones, calificaciones, comunicaciones) puedan determinar quién tiene acceso a qué.

Sin este change, no se pueden construir ni los equipos docentes (C-08), ni la ingesta de padrones (C-09), ni ningún módulo de FASE 4.

## What Changes

- **Enriquecer modelo `User`**: agregar campos de identidad (nombre, apellidos), PII cifrada (DNI, CUIL, CBU, alias CBU), banco, regional, legajo, legajo profesional, flag facturador, estado Activo/Inactivo.
- **Crear modelo `Asignacion`**: vincula Usuario ↔ Rol ↔ contexto académico (materia, carrera, cohorte, comisiones) con vigencia temporal y jerarquía (`responsable_id`).
- **ABM de usuarios** en `/api/admin/usuarios` con guard `usuarios:gestionar` (ADMIN).
- **CRUD de asignaciones** en `/api/asignaciones` con guard `equipos:asignar` (COORDINADOR, ADMIN).
- **Unicidad `(tenant_id, email)`** ya existe en el modelo actual, se mantiene.
- **Asignación vencida no otorga permisos** pero se conserva como histórico.
- **Migración 005**: alter `users` + crear `asignacion`.
- **Tests**: PII cifrada no expuesta en logs/respuestas, unicidad email por tenant, vigencia (vencida no autoriza), multi-rol, jerarquía responsable.
- Los campos PII se manejan con el helper `app/core/security.py` (AES-256-CBC) ya implementado en C-02.

## Capabilities

### New Capabilities
- `gestion-usuarios`: ABM de usuarios del tenant con PII cifrada, búsqueda por email, activación/desactivación.
- `gestion-asignaciones`: CRUD de asignaciones usuario ↔ rol ↔ contexto académico con vigencia y jerarquía.

### Modified Capabilities
Ninguna. No hay specs existentes en `openspec/specs/`.

## Impact

- **Modelos**: se modifica `models/user.py` (agrega campos), se crea `models/asignacion.py`.
- **Repositorios**: se crea `repositories/usuario.py` y `repositories/asignacion.py`.
- **Services**: se crea `services/usuario_service.py` y `services/asignacion_service.py`.
- **Routers**: se crea `routers/usuarios.py` y `routers/asignaciones.py` (nuevo directorio `routers/`).
- **Schemas**: se crea `schemas/usuarios.py` y `schemas/asignaciones.py`.
- **Migración**: nueva versión Alembic `005_usuario_asignacion`.
- **Tests**: archivos `tests/test_usuarios_models.py`, `tests/test_usuarios_endpoints.py`, `tests/test_asignaciones_models.py`, `tests/test_asignaciones_endpoints.py`.
