## ADDED Requirements

### Requirement: Listado de convocatorias (F7.4)
El sistema SHALL exponer un endpoint `GET /api/coloquios` que retorna lista paginada de evaluaciones (convocatorias) con métricas embebidas: materia, instancia, días disponibles, cantidad de alumnos convocados, reservas activas, cupos libres totales.

#### Scenario: Listar convocatorias exitosamente
- **WHEN** un COORDINADOR consulta GET /api/coloquios
- **THEN** el sistema retorna 200 con lista paginada de evaluaciones
- **AND** cada item incluye materia_nombre, instancia, tipo, dias_disponibles, total_convocados, total_reservas_activas, total_cupos_libres

#### Scenario: Listar convocatorias filtra por materia
- **WHEN** un COORDINADOR consulta GET /api/coloquios?materia_id={id}
- **THEN** el sistema retorna solo evaluaciones de esa materia

#### Scenario: Listar convocatorias sin datos retorna lista vacía
- **WHEN** no hay evaluaciones creadas
- **THEN** el sistema retorna 200 con lista vacía

#### Scenario: Listar convocatorias sin permiso retorna 403
- **WHEN** un ALUMNO consulta GET /api/coloquios
- **THEN** el sistema retorna 403

### Requirement: Agenda de reservas activas (F7.5)
El sistema SHALL exponer un endpoint `GET /api/coloquios/{id}/agenda` que retorna todas las reservas activas de una evaluación ordenadas por fecha, con datos del alumno (nombre, apellido, email) y día reservado.

#### Scenario: Consultar agenda exitosamente
- **WHEN** un COORDINADOR consulta GET /api/coloquios/{id}/agenda
- **THEN** el sistema retorna 200 con lista de reservas activas ordenadas por fecha
- **AND** cada item incluye: alumno_nombre, alumno_apellido, alumno_email, fecha_reserva

#### Scenario: Agenda sin reservas retorna lista vacía
- **WHEN** no hay reservas activas en la evaluación
- **THEN** el sistema retorna 200 con lista vacía

#### Scenario: Agenda sin permiso retorna 403
- **WHEN** un ALUMNO consulta GET /api/coloquios/{id}/agenda
- **THEN** el sistema retorna 403

### Requirement: Admin global — cerrar convocatoria (F7.5)
El sistema SHALL exponer un endpoint `PATCH /api/coloquios/{id}/cerrar` que permite a COORDINADOR/ADMIN cerrar una convocatoria. Al cerrar, no se permiten más reservas ni cancelaciones.

#### Scenario: Cerrar convocatoria exitosamente
- **WHEN** un COORDINADOR envía PATCH /api/coloquios/{id}/cerrar
- **THEN** el sistema retorna 200
- **AND** ya no se permiten nuevas reservas en esa evaluación
- **AND** se registra audit log COLOQUIO_CERRAR

#### Scenario: Cerrar convocatoria ya cerrada retorna error
- **WHEN** se intenta cerrar una convocatoria que ya está cerrada
- **THEN** el sistema retorna 400

#### Scenario: Cerrar convocatoria sin permiso retorna 403
- **WHEN** un ALUMNO envía PATCH /api/coloquios/{id}/cerrar
- **THEN** el sistema retorna 403

### Requirement: Admin global — editar convocatoria (F7.5)
El sistema SHALL exponer un endpoint `PATCH /api/coloquios/{id}` que permite a COORDINADOR/ADMIN modificar campos editables de una evaluación (instancia, dias_disponibles) siempre que no esté cerrada.

#### Scenario: Editar convocatoria exitosamente
- **WHEN** un COORDINADOR envía PATCH /api/coloquios/{id} con nuevos valores de instancia y dias_disponibles
- **THEN** el sistema retorna 200 con la evaluación actualizada

#### Scenario: Editar convocatoria cerrada retorna error
- **WHEN** se intenta editar una convocatoria cerrada
- **THEN** el sistema retorna 400 con mensaje "No se puede editar una convocatoria cerrada"

### Requirement: Alumno consulta convocatorias disponibles
El sistema SHALL exponer un endpoint `GET /api/coloquios/disponibles` que retorna las convocatorias activas donde el alumno autenticado está habilitado (en el padrón) y aún tiene días con cupo disponible.

#### Scenario: Alumno ve convocatorias disponibles
- **WHEN** un ALUMNO consulta GET /api/coloquios/disponibles
- **THEN** el sistema retorna 200 con lista de convocatorias donde está habilitado y hay cupo
- **AND** cada item incluye: materia_nombre, instancia, tipo, días_restantes con cupo
