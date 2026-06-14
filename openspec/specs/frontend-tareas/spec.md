## ADDED Requirements

### Requirement: Vista de mis tareas
La feature SHALL mostrar al docente las tareas asignadas a él desde `GET /api/tareas/mias`, con su estado, materia asociada y descripción.

#### Scenario: Listado de tareas propias
- **WHEN** el docente abre "Mis Tareas"
- **THEN** la feature renderiza las tareas asignadas con su estado actual

### Requirement: Administración global de tareas
La feature SHALL permitir al usuario con permiso `tareas:gestionar` ver todas las tareas del tenant desde `GET /api/tareas`, con filtros por docente asignado, docente asignador, materia, estado y búsqueda libre.

#### Scenario: Filtrado por estado y docente
- **WHEN** el coordinador aplica filtros de estado "En progreso" y un docente
- **THEN** la feature llama `GET /api/tareas` con esos query params y muestra solo las coincidencias

### Requirement: Alta y delegación de tareas
La feature SHALL permitir crear una tarea (`POST /api/tareas`) definiendo asignado, materia y descripción, dejando trazabilidad de asignador y asignado. El formulario SHALL validarse con React Hook Form + Zod.

#### Scenario: Alta de tarea con asignación
- **WHEN** el usuario crea una tarea y la asigna a otro docente
- **THEN** la feature envía el request, la tarea aparece con el asignado y asignador correctos e invalida el listado

### Requirement: Workflow de estados y comentarios en hilo
La feature SHALL permitir cambiar el estado de una tarea (`PATCH /api/tareas/{id}`) entre Pendiente / En progreso / Resuelta / Cancelada, y agregar/leer comentarios en hilo (`GET` y `POST /api/tareas/{id}/comentarios`) como parte del workflow asincrónico.

#### Scenario: Transición de estado
- **WHEN** el docente marca una tarea como "Resuelta"
- **THEN** la feature envía el PATCH, refleja el nuevo estado y refresca la tarea

#### Scenario: Comentario en hilo
- **WHEN** el usuario agrega un comentario a la tarea
- **THEN** la feature lo envía y lo muestra en el hilo sin recargar la página completa
