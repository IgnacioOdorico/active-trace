## 1. Repositorio — métodos de agregación

- [x] 1.1 Añadir `get_by_materia_con_entrada()` a `CalificacionRepository`: JOIN calificacion + entrada_padron para obtener datos completos del alumno (nombre, apellidos, email, comisión, regional)
- [x] 1.2 Añadir `get_estado_por_materia()`: retorna calificaciones con datos de entrada_padron, umbral y asignaciones para cómputo de atrasados
- [x] 1.3 Añadir `get_ranking_aprobadas()`: COUNT agrupado por entrada_padron_id de calificaciones con aprobado=true, filtrado a los que tienen ≥1
- [x] 1.4 Añadir `get_notas_por_alumno()`: calificaciones agrupadas por entrada_padron_id para una materia y lista de actividades
- [x] 1.5 Añadir `get_filtrado()`: consulta paginada con filtros dinámicos (materia_id, regional, comision, q, estado, desde, hasta, entrada_padron_id) para monitores

## 2. Service — AnalisisService

- [x] 2.1 Crear `services/analisis_service.py` con clase `AnalisisService` e inicialización de repositorios (CalificacionRepository, UmbralRepository, VersionPadronRepository, EntradaPadronRepository, AuditLogService)
- [x] 2.2 Implementar `atrasados()`: obtiene padrón activo + calificaciones + umbrales, computa alumnos atrasados por actividades faltantes o nota < umbral (RN-06, F2.2)
- [x] 2.3 Implementar `ranking()`: agrupa calificaciones por alumno, cuenta aprobado=true, excluye sin aprobadas, ordena descendente (RN-09, F2.3)
- [x] 2.4 Implementar `reportes_rapidos()`: métricas consolidadas de la materia (total_alumnos, total_actividades, total_calificaciones, promedio_aprobacion, atrasados/aprobados count) (F2.4)
- [x] 2.5 Implementar `notas_finales()`: promedio de nota_numerica por alumno para actividades seleccionadas, excluye textuales del promedio pero las lista como referencia (F2.5)
- [x] 2.6 Implementar `exportar_tps()`: cruza reporte de finalización contra calificaciones textuales sin nota, genera .xlsx con openpyxl (F2.6, RN-07/08)
- [x] 2.7 Implementar `monitor_general()`: vista transversal paginada con filtros (materia, regional, comision, q, estado) — scope global del tenant (F2.7)
- [x] 2.8 Implementar `monitor_seguimiento()`: vista filtrable scope por asignación del usuario (tutor/profesor: sus materias; coordinador/admin: global + rango fechas) (F2.8, F2.9)

## 3. Schemas

- [x] 3.1 Crear `schemas/analisis.py` con modelos Pydantic: AlumnoAtrasadoResponse, RankingItemResponse, ReportesResponse, NotaFinalItemResponse, MonitorItemResponse, MonitorPaginationResponse

## 4. Router

- [x] 4.1 Crear `routers/analisis.py` con APIRouter prefix `/api/analisis`, guard `atrasados:ver` en cada endpoint
- [x] 4.2 Endpoint GET `/api/analisis/atrasados/{materia_id}` — delega a AnalisisService.atrasados()
- [x] 4.3 Endpoint GET `/api/analisis/ranking/{materia_id}` — delega a AnalisisService.ranking()
- [x] 4.4 Endpoint GET `/api/analisis/reportes/{materia_id}` — delega a AnalisisService.reportes_rapidos()
- [x] 4.5 Endpoint POST `/api/analisis/notas-finales` — delega a AnalisisService.notas_finales()
- [x] 4.6 Endpoint GET `/api/analisis/exportar-tps/{materia_id}` — delega a AnalisisService.exportar_tps(), retorna StreamingResponse con .xlsx o JSON si no hay datos
- [x] 4.7 Endpoint GET `/api/analisis/monitor-general` — delega a AnalisisService.monitor_general()
- [x] 4.8 Endpoint GET `/api/analisis/monitor-seguimiento` — delega a AnalisisService.monitor_seguimiento()
- [x] 4.9 Registrar `analisis_router` en `app/main.py`

## 5. Tests

- [x] 5.1 Tests de atrasados: alumno sin actividades → atrasado, nota < umbral → atrasado, nota ≥ umbral → no atrasado, umbral por defecto 60%, sin padrón activo → 422
- [x] 5.2 Tests de ranking: solo alumnos con ≥1 aprobada, orden descendente, ranking vacío si nadie aprueba
- [x] 5.3 Tests de notas finales: promedio correcto, textuales excluidas del promedio, actividad no encontrada → 422
- [x] 5.4 Tests de monitores: filtro por materia, filtro por regional, filtro por comisión, búsqueda por q, paginación, scope por asignación del usuario
- [x] 5.5 Tests de export: genera .xlsx con datos, sin entregas retorna JSON informativo, solo incluye textuales, 403 sin permiso

## 6. Verificación

- [x] 6.1 `pytest` — todos los tests pasan
- [x] 6.2 `ruff check .` — sin errores en código nuevo
