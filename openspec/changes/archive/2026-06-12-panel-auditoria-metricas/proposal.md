## Why

The audit infrastructure (C-05) already captures every significant system action — pero no hay capa de analytics ni visualización. Administradores y coordinadores necesitan dashboards para monitorear volumen de uso temporal, estado de comunicaciones por docente, métricas de interacción por materia y docente, y un log de actividad reciente. Sin esto, la auditoría es un raw dump de datos sin valor analítico.

## What Changes

- **Nuevo router** `api/v1/routers/auditoria_panel.py` con endpoints de panel/analytics (separado del `audit.py` existente)
- **Nuevos métodos de agregación** en `AuditLogService`: `acciones_por_dia()`, `comunicaciones_por_docente()`, `interacciones_por_docente_materia()`, `ultimas_acciones()`
- **Nuevos métodos SQL de agregación** en `AuditLogRepository`
- **Scope `(propio)` para COORDINADOR**: filtra por materias donde tiene asignación activa
- **Sin migración DB**: solo consultas `SELECT` sobre la tabla `audit_log` existente
- **Sin nuevos modelos**: se reutiliza el modelo `AuditLog` existente

## Capabilities

### New Capabilities
- `panel-interacciones-sistema`: Endpoints de dashboard que exponen gráfico de acciones por día, estado de comunicaciones por docente, interacciones por docente y materia, y últimas acciones con filtros

### Modified Capabilities
- `audit-log-service`: Se agregan métodos públicos de agregación al `AuditLogService` (`acciones_por_dia`, `comunicaciones_por_docente`, `interacciones_por_docente_materia`, `ultimas_acciones`)

## Impact

- **API**: Nuevos endpoints bajo `/api/v1/admin/panel/` — no breaking, no cambios a endpoints existentes
- **Service layer**: `AuditLogService` se extiende con métodos nuevos — sin cambios a firma existente
- **Repository layer**: `AuditLogRepository` se extiende con consultas de agregación SQL
- **Permisos**: Se reutilizan permisos existentes (`auditoria:ver` / `auditoria:ver(propio)`)
- **Dependencias**: Ninguna nueva
