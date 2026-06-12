## 1. Repositorio — métodos de agregación SQL

- [x] 1.1 Agregar `acciones_por_dia()` en `AuditLogRepository`: `GROUP BY DATE(fecha_hora)` con `func.count()`, filtros por tenant, rango fechas, materia, actor, accion, y opcional `materias_ids` para scope `(propio)`
- [x] 1.2 Agregar `comunicaciones_por_docente()` en `AuditLogRepository`: filtrar acciones con prefijo `COMUNICACION_`, `GROUP BY actor_id`, contar por tipo de acción/estado
- [x] 1.3 Agregar `interacciones_por_docente_materia()` en `AuditLogRepository`: `GROUP BY actor_id, materia_id`, con `func.count()` total y desglose por tipo de acción
- [x] 1.4 Agregar `ultimas_acciones()` en `AuditLogRepository`: `ORDER BY fecha_hora DESC LIMIT :max` con los mismos filtros, retorna `Sequence[AuditLog]`

## 2. Servicio — métodos de agregación

- [x] 2.1 Agregar `acciones_por_dia()` en `AuditLogService`: delega al repositorio, recibe parámetros de filtro + `materias_ids: list[uuid.UUID] | None` para scope
- [x] 2.2 Agregar `comunicaciones_por_docente()` en `AuditLogService`: delega al repositorio, mismo patrón de filtros
- [x] 2.3 Agregar `interacciones_por_docente_materia()` en `AuditLogService`: delega al repositorio
- [x] 2.4 Agregar `ultimas_acciones()` en `AuditLogService`: delega al repositorio, cap `max_resultados` a 1000

## 3. Schemas Pydantic para responses del panel

- [x] 3.1 Crear `AccionesPorDiaItem` con `fecha: date` y `total: int`
- [x] 3.2 Crear `ComunicacionesPorDocenteItem` con `docente_id: str`, `docente_nombre: str`, `pendiente: int`, `enviando: int`, `enviado: int`, `fallido: int`, `cancelado: int`
- [x] 3.3 Crear `InteraccionesPorDocenteMateriaItem` con `docente_id: str`, `docente_nombre: str`, `materia_id: str`, `materia_nombre: str`, `total_acciones: int`, `acciones_por_tipo: dict`
- [x] 3.4 Crear `UltimasAccionesResponse` como wrapper de `list[AuditLogResponse]`

## 4. Router — panel de métricas

- [x] 4.1 Crear `backend/app/api/v1/routers/auditoria_panel.py` con `APIRouter(prefix="/api/v1/admin/panel", tags=["auditoria-panel"])`
- [x] 4.2 Implementar dependencia `_resolve_panel_permission` reutilizando `PermissionChecker` para `auditoria:ver` / `auditoria:ver(propio)`, con resolución de materias asignadas para COORDINADOR
- [x] 4.3 Implementar `GET /acciones-por-dia` con filtros `desde`, `hasta`, `materia_id`, `actor_id`, `accion` y scoping
- [x] 4.4 Implementar `GET /comunicaciones-por-docente` con filtros `desde`, `hasta`, `materia_id` y scoping
- [x] 4.5 Implementar `GET /interacciones-por-docente-materia` con filtros `desde`, `hasta`, `materia_id`, `actor_id` y scoping
- [x] 4.6 Implementar `GET /ultimas-acciones` con filtros `max` (default 200, max 1000), `desde`, `hasta`, `materia_id`, `actor_id`, `accion` y scoping
- [x] 4.7 Registrar el router en la aplicación principal (`backend/app/main.py`)

## 5. Tests

- [x] 5.1 Tests de existencia de métodos de agregación en `AuditLogRepository` (verificación de que tienen los 4 métodos nuevos)
- [x] 5.2 Tests de existencia de métodos nuevos en `AuditLogService` + verificación de delegación y cap de max_resultados
- [x] 5.3 Tests de integración para cada endpoint del panel (happy path con mock DB + verificación de paths registrados + estructura de respuesta)
- [x] 5.4 Tests de permisos: 401 sin auth, 403/401 sin token válido
