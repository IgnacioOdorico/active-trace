## Context

C-07 (`usuarios-y-asignaciones`) estableció el modelo de asignaciones docentes con roles (PROFESOR, TUTOR, COORDINADOR, etc.) y contexto académico. Sobre esa base, este change implementa la gestión de evaluaciones y coloquios (F7.1–F7.5, FL-07): los coordinadores necesitan crear convocatorias de coloquio con cupos limitados, importar alumnos habilitados, y que los alumnos reserven su turno en días disponibles. Adicionalmente, se registran resultados académicos consolidados.

El proyecto ya cuenta con:
- `EntityMeta` mixin en `backend/app/models/base.py` con `id` UUID, `tenant_id` FK, `created_at`, `updated_at`, `deleted_at`.
- `BaseRepository` en `backend/app/repositories/base.py` con filtro `tenant_id` automático, soft delete, paginación.
- `AuditLogService` en `backend/app/services/audit_service.py` con constantes de acción.
- Patrón Clean Architecture consolidado: Models → Repositories → Services → Routers.
- Guard `require_permission("modulo:accion")` en `app/core/permissions.py`.
- C-13 (`encuentros-y-guardias`) como referencia del mismo patrón de negocio con slots, reservas y cupos.

## Goals / Non-Goals

**Goals:**
- Modelos ORM `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion` con `EntityMeta` y SQLAlchemy 2.0 async.
- Creación de convocatoria de coloquio (F7.3): definir materia, instancia, días disponibles y cupos por día.
- Importar alumnos a convocatoria (F7.2): carga/actualiza padrón de alumnos habilitados para una evaluación.
- Reserva de turno por alumno (FL-07): selecciona día disponible con cupo > 0, reserva decrementa cupo. Solo ALUMNO puede reservar.
- Cancelación de reserva: estado Activa → Cancelada, libera cupo.
- Listado de convocatorias (F7.4): vista tabular con métricas por convocatoria.
- Panel de métricas (F7.1): total alumnos cargados, instancias activas, reservas activas, notas registradas.
- Admin global (F7.5): gestión de convocatorias (alta, edición, cierre), registro académico consolidado, agenda de reservas activas.
- Endpoints REST `/api/coloquios/*` con guards `coloquios:gestionar` y `coloquios:reservar`.
- Audit log con códigos `COLOQUIO_CREAR`, `COLOQUIO_RESERVAR`, `COLOQUIO_CERRAR`.
- Tests de creación de turnos con cupo, reserva resta cupo, sin cupo rechaza, métricas, resultado consolidado.

**Non-Goals:**
- No se implementa frontend de coloquios.
- No se implementa notificación automática al confirmar/cancelar reserva.
- No se implementa integración con calendario (iCalendar, Google Calendar).
- No se implementa edición masiva de reservas.
- No se implementa recuperación de contraseña ni reenvío de confirmación.

## Decisions

### D1: Turnos con cupo — slot de tiempo en la evaluación
- **Decisión**: Al crear una `Evaluacion` con `dias_disponibles` y cupos, el sistema almacena los días como fechas concretas en una tabla separada `evaluacion_dia` (día fecha, cupo_maximo, cupos_restantes). Se genera un registro por día hábil dentro de la ventana definida.
- **Alternativa considerada**: Almacenar días como rango (fecha_desde + fecha_hasta) sin slots individuales.
- **Razón**: El control de cupo requiere granularidad por día. Con un registro por día podemos decrementar `cupos_restantes` atómicamente con una UPDATE condicional (`WHERE cupos_restantes > 0`). El rango simple no permite saber si el lunes ya no tiene cupo pero el martes sí.

### D2: Reserva con decremento atómico de cupo
- **Decisión**: Al reservar, se ejecuta UPDATE `evaluacion_dia SET cupos_restantes = cupos_restantes - 1 WHERE id = :dia_id AND cupos_restantes > 0`. Si `rowcount = 0`, se rechaza con error "cupo agotado". Luego se INSERT la `ReservaEvaluacion`. Todo en la misma transacción.
- **Alternativa considerada**: Leer cupo actual en Python, comparar, escribir.
- **Razón**: La UPDATE condicional en SQL es atómica y evita race conditions. Dos usuarios reservando el último cupo simultáneamente: solo uno obtiene rowcount=1. El enfoque en Python tiene una ventana TOCTOU.

### D3: Solo ALUMNO puede reservar (verificado por rol + permiso)
- **Decisión**: El endpoint `POST /api/coloquios/{id}/reservar` verifica:
  1. El usuario autenticado tiene rol `ALUMNO` (vía `get_current_user().rol == "ALUMNO"`)
  2. El usuario tiene permiso `coloquios:reservar`
  3. El alumno está en el padrón de la evaluación
- **Alternativa considerada**: Delegar toda la verificación al permiso.
- **Razón**: El permiso `coloquios:reservar` solo puede tenerlo ALUMNO por definición, pero la doble verificación (rol + permiso) es defensiva. La verificación de padrón evita que un alumno no habilitado reserve.

### D4: Modelo Evaluacion como cabecera de convocatoria
- **Decisión**: `Evaluacion` es la cabecera con datos generales (materia, cohorte, tipo, instancia). Los días con cupo van en `EvaluacionDia` (1:N). Las reservas van en `ReservaEvaluacion` apuntando a `EvaluacionDia`. Los resultados van en `ResultadoEvaluacion` apuntando a `Evaluacion`.
- **Alternativa considerada**: Todo en una sola tabla con columnas JSON para días.
- **Razón**: Separación de responsabilidades. Las consultas SQL son simples y tipadas. El control de cupo es eficiente. Cada tabla tiene su propio ciclo de vida (ej: se pueden agregar más días a una evaluación sin tocar las reservas existentes).

### D5: Dos permisos — `coloquios:gestionar` y `coloquios:reservar`
- **Decisión**:
  - `coloquios:gestionar`: COORDINADOR, ADMIN — CRUD de convocatorias, importación, métricas, admin global.
  - `coloquios:reservar`: ALUMNO — reservar/cancelar su turno, ver sus reservas.
- **Alternativa considerada**: Un solo permiso `coloquios:*` gestionado por roles.
- **Razón**: La separación refleja dos contextos de uso muy distintos: gestión (coordinación) y reserva (alumno). Sigue el patrón ya establecido en el proyecto de permisos finos por módulo:acción. Si un día se quiere delegar gestión a un rol nuevo, no hay que tocar permisos existentes.

### D6: Importación de alumnos como reemplazo de padrón completo
- **Decisión**: Al importar alumnos a una evaluación, se reemplaza TODO el padrón actual. El endpoint `POST /api/coloquios/{id}/alumnos` recibe una lista de `alumno_id` y hace un reemplazo atómico: DELETE de alumnos existentes + INSERT de los nuevos, en transacción.
- **Alternativa considerada**: Importación incremental (agregar/quitar individualmente).
- **Razón**: El caso de uso es "el profesor prepara la lista de candidatos al coloquio". Siempre sube la lista completa actualizada. El reemplazo atómico evita tener que hacer diff manual. Si se necesita granularidad fina en el futuro, se puede agregar un endpoint PATCH.

### D7: ResultadoEvaluacion con nota_final como texto
- **Decisión**: `nota_final` es `String(20)` para soportar tanto valores numéricos ("8", "10") como cualitativos ("Aprobado", "Ausente", "Recursa").
- **Alternativa considerada**: Columna numérica `Float` para nota y `String` aparte para concepto.
- **Razón**: Las actas académicas pueden tener valores no numéricos (Ausente, Libre, etc.). Almacenar como texto evita problemas de parseo y mantiene flexibilidad. La interpretación del valor es responsabilidad de la capa de presentación.

## Risks / Trade-offs

- **[Riesgo] Race condition en reserva simultánea del último cupo**: dos alumnos reservan el último cupo al mismo tiempo. → **Mitigación**: UPDATE condicional con `WHERE cupos_restantes > 0` y verificación de `rowcount` en la misma transacción (D2). Es atómico en PostgreSQL.
- **[Riesgo] Importación de alumnos elimina padrón existente**: si la llamada de importación falla a mitad del proceso, se pierde el padrón. → **Mitigación**: todo en una transacción. Si falla el INSERT después del DELETE, el DELETE se revierte automáticamente.
- **[Riesgo] Fecha/hora de reserva sin validación de superposición**: un alumno podría tener dos reservas en el mismo horario en distintas evaluaciones. → **Mitigación**: no se considera un problema en este alcance (el alumno gestiona su agenda). Si se requiere en el futuro, se agrega validación en el servicio.
- **[Trade-off] nota_final como texto**: pierde capacidad de cómputo numérico directo. → **Razón**: se prioriza flexibilidad de tipos de acta sobre capacidad de cálculo. Si se necesitan promedios, la capa de presentación puede parsear valores numéricos.
