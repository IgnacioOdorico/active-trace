## Why

C-07 ya creó el modelo `Asignacion` que vincula usuario ↔ rol ↔ contexto académico. Ahora hace falta la capa de negocio sobre ese modelo: que los docentes puedan ver sus equipos, que los coordinadores puedan asignar docentes en bloque, clonar equipos entre períodos, modificar vigencias y exportar. Sin esto, las asignaciones son solo datos — no hay operaciones útiles para el usuario.

## What Changes

- **Vista "mis equipos"** (F4.2): endpoint que devuelve las asignaciones del usuario autenticado, con filtros por estado, materia, rol, carrera, cohorte.
- **Asignación masiva** (F4.4): endpoint para seleccionar múltiples docentes y asignarlos en bloque a materia × carrera × cohorte × rol con vigencia.
- **Clonar equipo entre períodos** (F4.5, RN-12): duplica asignaciones vigentes de un origen (materia × carrera × cohorte) a un destino con nuevas fechas.
- **Modificar vigencia general** (F4.6): actualiza `desde`/`hasta` de todas las asignaciones de un equipo en una operación.
- **Exportar equipo** (F4.7): genera archivo descargable con detalle de asignaciones del equipo.
- **Audit `ASIGNACION_MODIFICAR`** en operaciones de escritura.
- Endpoints bajo `/api/equipos/*` con guard `equipos:asignar` (COORDINADOR, ADMIN).
- Posible uso de la skill `xlsx` para la exportación.

## Capabilities

### New Capabilities
- `gestion-equipos`: operaciones de negocio sobre asignaciones — vista propia, asignación masiva, clonado, vigencia, exportación.

### Modified Capabilities
- `gestion-asignaciones` (de C-07): se agregan las operaciones masivas y de negocio sobre las asignaciones existentes.

## Impact

- **Modelos**: no se crean modelos nuevos — se reutiliza `Asignacion` de C-07.
- **Repositorios**: se extiende `AsignacionRepository` con métodos para clonado, asignación masiva, modificación en bloque.
- **Services**: se crea `services/equipo_service.py` con lógica de clonado (RN-12), asignación masiva, modificación de vigencia.
- **Routers**: se crea `routers/equipos.py` con endpoints bajo `/api/equipos/*`.
- **Schemas**: se crean schemas específicos para operaciones masivas (`schemas/equipos.py`).
- **Tests**: clonado entre cohortes, asignación masiva, modificación de vigencia en bloque, export.
- **Skill `xlsx`**: posiblemente necesaria para exportar a Excel.
