## Context

C-07 (`usuarios-y-asignaciones`) estableció el modelo de usuarios y asignaciones que este change necesita como contexto de actores (asignado_a, asignado_por). El proyecto ya cuenta con EntityMeta mixin, BaseRepository, AuditLogService, y el patrón Clean Architecture consolidado. Sobre esa base, este change implementa Épica 8 (F8.1–F8.3) + FL-05: un sistema de tareas internas con asignación, seguimiento y comentarios.

## Goals / Non-Goals

**Goals:**
- Modelos ORM `Tarea` y `ComentarioTarea` con `EntityMeta`.
- Asignación de tareas con trazabilidad (asignado_a, asignado_por).
- Workflow de estados: Pendiente → En progreso → Resuelta, más Cancelada desde cualquier estado activo.
- Hilo de comentarios por tarea (orden cronológico, autor visible).
- Vista "mis tareas" para el docente asignado (F8.1).
- Vista global con filtros para coordinación (F8.3).
- Delegación entre docentes (F8.2): reasignar tarea a otro usuario.
- Endpoints REST `/api/tareas/*` con guard `tareas:gestionar`.

**Non-Goals:**
- No se implementa frontend de tareas (solo API).
- No se implementan notificaciones al asignar/modificar tareas.
- No se implementan tareas recurrentes ni programadas.
- No se implementa adjuntos/archivos en comentarios.

## Decisions

### D1: Estado como String(20) con enum Python
- **Decisión**: `estado` se almacena como String(20) con enum Python `EstadoTarea` (Pendiente, En progreso, Resuelta, Cancelada).
- **Razón**: Consistencia con el resto del modelo (Comunicacion.estado, InstanciaEncuentro.estado, etc.).

### D2: Transiciones de estado explícitas
- **Decisión**: Pendiente → {En progreso, Cancelada}; En progreso → {Resuelta, Cancelada}; Resuelta y Cancelada son estados terminales.
- **Razón**: El workflow es simple pero requiere control. Una vez resuelta o cancelada, no se puede reabrir.

### D3: Todos los roles pueden comentar en tareas donde son parte
- **Decisión**: El asignado, el asignador y COORDINADOR/ADMIN pueden agregar comentarios a una tarea. Se verifica que el usuario tenga relación con la tarea.
- **Razón**: El hilo de comentarios es colaborativo. Restringir solo al asignado limitaría la comunicación.

### D4: Reasignación como edición del campo asignado_a
- **Decisión**: El endpoint PATCH permite cambiar `asignado_a`. Registra el cambio en audit log.
- **Razón**: Simplicidad. No se necesita un modelo separado de delegación. La trazabilidad queda en audit log.

### D5: Búsqueda libre con ILIKE sobre descripción
- **Decisión**: El endpoint de administración global permite búsqueda libre por texto en `descripcion` usando ILIKE.
- **Razón**: Es el campo más relevante para búsqueda. Si se necesita más granularidad en el futuro, se puede extender.

### D6: Contexto_id como referencia opcional genérica
- **Decisión**: `contexto_id` es un UUID nullable que referencia a otra entidad del dominio (ej: materia_id, aviso_id). No tiene FK declarativa.
- **Razón**: Flexibilidad. Permite asociar tareas a diferentes entidades sin acoplar el modelo.

## Risks / Trade-offs

- **[Riesgo] Volumen de comentarios**: módulo de alto uso, cientos de tareas simultáneas con múltiples comentarios. → **Mitigación**: paginación en comentarios, límite de 50 por página.
- **[Trade-off] Sin notificaciones**: el usuario no recibe alerta cuando se le asigna una tarea o recibe un comentario. → **Razón**: las notificaciones se implementarán en un change futuro (posiblemente C-20 mensajería o un módulo de notificaciones dedicado).
