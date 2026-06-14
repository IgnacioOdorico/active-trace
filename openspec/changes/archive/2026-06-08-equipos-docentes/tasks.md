## 1. Service layer

- [x] 1.1 Crear `services/equipo_service.py` con método `listar_mis_equipos` (filtra por usuario autenticado)
- [x] 1.2 Implementar `asignacion_masiva` — crea múltiples asignaciones en una transacción
- [x] 1.3 Implementar `clonar_equipo` — duplica asignaciones vigentes entre cohortes (RN-12) con FOR UPDATE
- [x] 1.4 Implementar `modificar_vigencia` y `modificar_vigencia_masiva`
- [x] 1.5 Implementar `exportar_equipo` — genera archivo .xlsx en memoria
- [x] 1.6 Integrar audit `ASIGNACION_MODIFICAR` en todas las operaciones de escritura

## 2. Schemas

- [x] 2.1 Crear `schemas/equipos.py` — AsignacionMasivaRequest, ClonarRequest, VigenciaRequest, EquipoExportResponse

## 3. Router

- [x] 3.1 Crear `routers/equipos.py` con GET /api/equipos/mis-equipos (guard `equipos:asignar`)
- [x] 3.2 Implementar POST /api/equipos/asignacion-masiva
- [x] 3.3 Implementar POST /api/equipos/clonar
- [x] 3.4 Implementar PATCH /api/equipos/{id}/vigencia y PATCH /api/equipos/vigencia-masiva
- [x] 3.5 Implementar GET /api/equipos/{id}/exportar
- [x] 3.6 Registrar router en `app/main.py`

## 4. Tests

- [x] 4.1 Tests de servicio: asignación masiva, clonado, modificación vigencia
- [x] 4.2 Tests de endpoints: permisos (403), clonado, export
- [x] 4.3 Test de audit: cada operación de escritura genera ASIGNACION_MODIFICAR

## 5. Verificación

- [x] 5.1 `pytest` — todos los tests pasan
- [x] 5.2 `ruff check .` — sin errores
