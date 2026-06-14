## ADDED Requirements

### Requirement: Audit log para creación de convocatoria
El sistema SHALL registrar un evento en el audit log con código `COLOQUIO_CREAR` cuando un COORDINADOR/ADMIN crea una nueva convocatoria (Evaluacion).

#### Scenario: Crear convocatoria registra audit log
- **WHEN** un COORDINADOR crea una convocatoria exitosamente
- **THEN** el sistema registra en audit log: accion="COLOQUIO_CREAR", usuario_id del creador, entidad="evaluacion", entidad_id del UUID creado

### Requirement: Audit log para reserva de turno
El sistema SHALL registrar un evento en el audit log con código `COLOQUIO_RESERVAR` cuando un ALUMNO reserva un turno exitosamente.

#### Scenario: Reservar turno registra audit log
- **WHEN** un ALUMNO reserva un turno exitosamente
- **THEN** el sistema registra en audit log: accion="COLOQUIO_RESERVAR", usuario_id del alumno, entidad="reserva_evaluacion", entidad_id del UUID creado

#### Scenario: Cancelar reserva registra audit log
- **WHEN** un ALUMNO cancela su reserva exitosamente
- **THEN** el sistema registra en audit log: accion="COLOQUIO_RESERVAR", usuario_id del alumno, entidad="reserva_evaluacion", entidad_id, detalle="cancelada"

### Requirement: Audit log para cierre de convocatoria
El sistema SHALL registrar un evento en el audit log con código `COLOQUIO_CERRAR` cuando un COORDINADOR/ADMIN cierra una convocatoria.

#### Scenario: Cerrar convocatoria registra audit log
- **WHEN** un COORDINADOR cierra una convocatoria exitosamente
- **THEN** el sistema registra en audit log: accion="COLOQUIO_CERRAR", usuario_id del coordinador, entidad="evaluacion", entidad_id

### Requirement: Constantes COLOQUIO en AuditLogService
El sistema SHALL agregar las constantes `COLOQUIO_CREAR`, `COLOQUIO_RESERVAR` y `COLOQUIO_CERRAR` en `AuditLogService` como atributos de clase con sus valores string correspondientes.

#### Scenario: Constantes disponibles en AuditLogService
- **WHEN** se importa AuditLogService
- **THEN** las constantes `COLOQUIO_CREAR`, `COLOQUIO_RESERVAR`, `COLOQUIO_CERRAR` están disponibles como atributos de clase
