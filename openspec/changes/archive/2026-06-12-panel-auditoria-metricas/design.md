## Context

El sistema ya cuenta con infraestructura completa de auditoría (C-05): modelo `AuditLog` append-only, repositorio con listado paginado y filtros, servicio con decorador/helper, y router `GET /api/v1/admin/audit-log` con filtros y scoping por permiso `auditoria:ver` / `auditoria:ver(propio)`.

Sin embargo, no existe una capa analítica sobre estos datos. Los administradores y coordinadores necesitan dashboards para monitorear volumen de uso, estado de comunicaciones, métricas por docente/materia y un log de últimas acciones — todo sobre la misma tabla `audit_log`, sin nuevos modelos ni migraciones.

## Goals / Non-Goals

**Goals:**
- Proveer endpoints de agregación/dashboard para el panel de auditoría
- Implementar scoping correcto: COORDINADOR solo ve materias donde tiene asignación activa
- Extender `AuditLogService` y `AuditLogRepository` con métodos de agregación SQL
- Separar el router de panel del router admin existente (`audit.py`)
- Sin migraciones ni modelos nuevos

**Non-Goals:**
- No incluye frontend/UI — solo API REST
- No modifica endpoints existentes de auditoría
- No agrega nuevas acciones al catálogo de códigos
- No implementa caché (queda para optimización futura si es necesario)

## Decisions

### D1: Router separado para panel de métricas
**Opción A (elegida):** Nuevo router `auditoria_panel.py` en `api/v1/routers/`
**Opción B:** Agregar endpoints al router `audit.py` existente
**Por qué A:** `audit.py` maneja admin log + impersonación; los endpoints de panel son cualitativamente distintos (analytics vs raw log). Separar mantiene cohesión y facilita evolución independiente. Las rutas se registran bajo `/api/v1/admin/panel/`.

### D2: Agregación en SQL vía el repositorio
**Opción A (elegida):** `AuditLogRepository` expone métodos que retornan resultados de agregación usando `func.count()`, `func.date_trunc()`, `func.json_agg()` de SQLAlchemy
**Opción B:** Extraer datos crudos y agregar en memoria (Python)
**Por qué A:** La tabla `audit_log` puede crecer significativamente. Agregar en SQL minimiza transferencia de datos y aprovecha índices existentes en `(tenant_id, fecha_hora)` y `(tenant_id, accion)`.

### D3: Scope `(propio)` para COORDINADOR — filtro por materias asignadas
**Opción A (elegida):** El servicio recibe `materias_ids: list[uuid.UUID] | None`. Si es COORDINADOR, se inyectan las materias donde tiene asignación activa (obtenidas del sistema de asignaciones existente). Si es ADMIN, `materias_ids=None` = sin filtro de materia.
**Opción B:** El COORDINADOR ve solo sus propias acciones (como en el audit-log actual)
**Por qué A:** El feature FL-11 específicamente pide que COORDINADOR supervise actividad de docentes en sus materias, no solo la propia. El `(propio)` se refiere a las materias donde tiene asignación, no a sus acciones como actor.

### D4: Método unificado `ultimas_acciones` con límite configurable
Se expone con `max_resultados: int = 200` (configurable por query param). Internamente usa `ORDER BY fecha_hora DESC LIMIT :max` sobre la tabla audit_log filtrada. Máximo absoluto: 1000 para evitar abusos.

### D5: Estado de actividad se deriva del audit_log
**Opción:** Se consulta la última acción del usuario en el rango de fechas. Si la última acción es anterior a N días (configurable, default 30), se marca como `inactivo`. Esto evita depender de `user.updated_at` que puede no reflejar actividad en el sistema.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| **Performance**: consultas `GROUP BY` sobre `audit_log` con millones de filas pueden ser lentas | Endpoints requieren rango de fechas obligatorio o tienen default acotado (últimos 30 días). Índices compuestos existentes en `(tenant_id, fecha_hora)` cubren el filtro principal |
| **Exactitud de comunicación**: el estado "Enviando/Enviado/Fallido" se deriva de acciones de auditoría (`COMUNICACION_ENVIAR`, etc.) y puede no reflejar el estado actual real de la comunicación | Es un panel informativo/analítico, no un reemplazo del estado real. Se documenta que los datos son históricos basados en audit_log |
| **Scope `(propio)`**: la resolución de materias asignadas requiere consultar el sistema de asignaciones, potencialmente costoso | La lista de materias se pasa como parámetro; el servicio de panel no resuelve asignaciones. El router inyecta las materias desde el servicio de asignaciones existente |
