## Why

Los equipos docentes necesitan un mecanismo de coordinación interna para asignar, dar seguimiento y resolver tareas entre roles (COORDINADOR → PROFESOR/TUTOR, o entre pares). Hoy no existe trazabilidad de estas comunicaciones: todo se maneja por canales externos (WhatsApp, email) sin registro ni accountability. Este change implementa la Épica 8 completa (F8.1–F8.3) + FL-05: un sistema liviano de tareas con asignación, comentarios en hilo y workflow de estados.

## What Changes

- Modelos `Tarea` y `ComentarioTarea` con EntityMeta y SQLAlchemy 2.0 async.
- Mis tareas (F8.1): endpoint que lista las tareas asignadas al usuario autenticado, con filtros por estado, materia.
- Asignar tarea (F8.2): creación de tarea con asignado_a (docente destino), descripción, materia opcional. Trazabilidad de asignador/origen.
- Administración global (F8.3): listado completo del tenant con filtros (docente, materia, estado, búsqueda libre) para COORDINADOR/ADMIN.
- Cambio de estado + comentarios: workflow asincrónico con hilo de comentarios por tarea (Pendiente → En progreso → Resuelta → Cancelada).
- Endpoints REST `/api/tareas/*` con guard `tareas:gestionar`.
- Audit log con códigos `TAREA_CREAR`, `TAREA_EDITAR`, `TAREA_COMENTAR`.
- Migración Alembic con tablas `tarea` y `comentario_tarea`.

## Capabilities

### New Capabilities
- `modelo-tareas`: modelos ORM Tarea y ComentarioTarea con EntityMeta, enum EstadoTarea (Pendiente/En progreso/Resuelta/Cancelada)
- `crud-tareas`: ABM de tareas con asignación, trazabilidad asignador/asignado, contexto opcional
- `mis-tareas`: listado de tareas asignadas al usuario con filtros
- `admin-tareas`: listado global del tenant con filtros (docente, materia, estado, búsqueda)
- `comentarios-tarea`: hilo de comentarios por tarea, workflow asincrónico
- `audit-tareas`: registro de auditoría con códigos TAREA_CREAR, TAREA_EDITAR, TAREA_COMENTAR

### Modified Capabilities
- *(ninguna — todas son nuevas)*

## Impact

- **Models**: nuevos `backend/app/models/tarea.py`, `comentario_tarea.py` — ambos con EntityMeta.
- **Repositories**: `TareaRepository` (con filtros por asignado/materia/estado, búsqueda libre) y `ComentarioTareaRepository` (CRUD por tarea).
- **Services**: nuevo `TareaService` con lógica de ABM, filtros, cambio de estado, comentarios.
- **Routers**: nuevo `routers/tareas.py` bajo `/api/tareas/*`.
- **Schemas**: nuevo `schemas/tarea.py` con modelos Pydantic para request/response.
- **Permisos**: crear permiso `tareas:gestionar` en el catálogo (asignado a COORD, ADMIN, PROFESOR).
- **Migración**: nueva migración Alembic con 2 tablas: `tarea`, `comentario_tarea`.
