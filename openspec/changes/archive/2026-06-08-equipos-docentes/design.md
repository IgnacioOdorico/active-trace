## Context

C-07 implementó el modelo `Asignacion` con CRUD básico en `/api/asignaciones`. Ahora necesitamos la capa de negocio sobre ese modelo: vistas propias del docente, operaciones masivas (COORDINADOR/ADMIN), clonado entre períodos, modificación de vigencia en bloque y exportación.

El modelo `Asignacion` ya tiene: usuario_id, rol, materia_id, carrera_id, cohorte_id, comisiones, responsable_id, desde, hasta. No se requieren cambios al modelo.

## Goals / Non-Goals

**Goals:**
- Endpoint `GET /api/equipos/mis-equipos` para el usuario autenticado (F4.2).
- Endpoint `POST /api/equipos/asignacion-masiva` para asignar múltiples docentes en bloque (F4.4).
- Endpoint `POST /api/equipos/clonar` para duplicar equipo entre cohortes (F4.5, RN-12).
- Endpoint `PATCH /api/equipos/{id}/vigencia` para modificar vigencia general (F4.6).
- Endpoint `GET /api/equipos/{id}/exportar` para exportar equipo a archivo (F4.7).
- Audit `ASIGNACION_MODIFICAR` en cada operación de escritura.
- Tests de clonado, asignación masiva, modificación de vigencia, export.

**Non-Goals:**
- No se modifican los endpoints CRUD de `/api/asignaciones` creados en C-07.
- No se implementa la interfaz de usuario (frontend).
- No se implementa la importación de padrón (eso es C-09).

## Decisions

### D1: Un solo `EquipoService` para todas las operaciones
- **Decisión**: Centralizar toda la lógica de equipos en `services/equipo_service.py`.
- **Razón**: Todas las operaciones operan sobre el mismo modelo `Asignacion`. Tener un service cohesivo evita duplicación.

### D2: Clonado como transacción
- **Decisión**: La operación de clonado se ejecuta dentro de una transacción SQL. Si falla una asignación, no se persiste ninguna.
- **Alternativa considerada**: Clonado asincrónico con worker.
- **Razón**: El volumen de asignaciones por equipo es bajo (decenas, no miles). Una transacción sincrónica es más simple y predecible.

### D3: Exportación como generación de archivo temporal
- **Decisión**: El endpoint `GET /api/equipos/{id}/exportar` genera un archivo `.xlsx` en memoria y lo devuelve como `StreamingResponse`.
- **Razón**: No requiere almacenamiento en disco ni limpieza posterior. La skill `xlsx` se usará para formatear el archivo.

## Risks / Trade-offs

- **[Riesgo] Clonado con datos inconsistentes**: si entre la lectura y la escritura cambian las asignaciones origen. → **Mitigación**: la transacción usa `SELECT ... FOR UPDATE` para bloquear las filas origen.
- **[Trade-off] Sin paginación en exportación**: el archivo incluye todo el equipo. Para equipos muy grandes (>1000 asignaciones) podría ser lento. → Se acepta; el volumen típico es <100 por equipo.
