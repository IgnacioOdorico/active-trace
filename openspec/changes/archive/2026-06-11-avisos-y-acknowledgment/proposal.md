## Why

El sistema necesita un mecanismo de comunicación institucional dirigido y controlado. Hoy no hay forma de que COORDINADOR o ADMIN publiquen novedades (cambios de calendario, suspensiones, comunicados urgentes) segmentadas por audiencia (rol, materia, cohorte). Tampoco existe trazabilidad de lectura para avisos críticos. Este change implementa la Épica 3.5 (tablón de avisos) + FL-09, cubriendo el ciclo completo: publicar → segmentar → visualizar → acusar recibo.

## What Changes

- Modelos `Aviso` y `AcknowledgmentAviso` con EntityMeta y SQLAlchemy 2.0 async.
- ABM de avisos con alcance (Global/PorMateria/PorCohorte/PorRol), severidad (Info/Advertencia/Crítico), vigencia programada (`inicio_en`/`fin_en`), orden de prioridad, y requerimiento opcional de acuse de recibo.
- Endpoint de visualización que filtra avisos según el perfil del usuario autenticado (tenant, rol, materias/cohortes asignadas, ventana de vigencia).
- Endpoint de confirmación de lectura (acknowledgment) con idempotencia y contadores derivados desde la tabla (no denormalizados).
- Endpoints REST `/api/avisos/*` con permisos `avisos:publicar` (ABM) y `avisos:ver` (lectura).
- Audit log con códigos `AVISO_PUBLICAR`, `AVISO_EDITAR`, `AVISO_ELIMINAR`.
- Migración Alembic con tablas `aviso` y `acknowledgment_aviso`.

## Capabilities

### New Capabilities
- `modelo-avisos`: modelos ORM Aviso y AcknowledgmentAviso con EntityMeta, enums AlcanceAviso (Global/PorMateria/PorCohorte/PorRol) y SeveridadAviso (Info/Advertencia/Crítico)
- `crud-avisos`: ABM de avisos con alcance, severidad, vigencia programada, orden, activo/inactivo, requiere_ack
- `visualizar-avisos`: filtrado server-side de avisos visibles según perfil del usuario (tenant, rol, materias, cohortes, vigencia)
- `acknowledgment-avisos`: confirmación de lectura con idempotencia, contadores derivados
- `audit-avisos`: registro de auditoría con códigos `AVISO_PUBLICAR`, `AVISO_EDITAR`, `AVISO_ELIMINAR`

### Modified Capabilities
- *(ninguna — todas son nuevas)*

## Impact

- **Models**: nuevos `backend/app/models/aviso.py`, `acknowledgment_aviso.py` — ambos con EntityMeta mixin.
- **Repositories**: nuevos `AvisoRepository` (con filtros por perfil/vigencia/rol) y `AcknowledgmentAvisoRepository` (con conteo y upsert).
- **Services**: nuevo `AvisoService` con lógica de ABM, filtrado por perfil, acknowledgment.
- **Routers**: nuevo `routers/avisos.py` bajo `/api/avisos/*`.
- **Schemas**: nuevo `schemas/aviso.py` con modelos Pydantic para request/response.
- **Permisos**: crear permisos `avisos:publicar` y `avisos:ver` en el catálogo.
- **Migración**: nueva migración Alembic con 2 tablas: `aviso`, `acknowledgment_aviso`.
- **Tests**: ABM avisos, filtrado por scope/vigencia, acknowledgment, contadores, permisos.
