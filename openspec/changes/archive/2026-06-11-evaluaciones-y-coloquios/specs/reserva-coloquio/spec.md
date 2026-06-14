## ADDED Requirements

### Requirement: Alumno reserva turno (FL-07)
El sistema SHALL exponer un endpoint `POST /api/coloquios/{id}/reservar` que permita a un ALUMNO habilitado reservar un turno en un día específico de la convocatoria. El endpoint recibe `evaluacion_dia_id`. El sistema verifica: (1) el usuario tiene rol ALUMNO y permiso `coloquios:reservar`, (2) el alumno está en el padrón de la evaluación, (3) el día tiene cupo disponible. Si todo OK, decrementa cupo_restantes y crea la ReservaEvaluacion en una transacción.

#### Scenario: Reservar turno exitosamente
- **WHEN** un ALUMNO habilitado envía POST /api/coloquios/{id}/reservar con evaluacion_dia_id válido y cupo_restantes > 0
- **THEN** el sistema retorna 201 con la reserva creada (estado "Activa")
- **AND** cupo_restantes del día se decrementa en 1

#### Scenario: Reservar sin cupo disponible retorna error
- **WHEN** un ALUMNO intenta reservar en un día con cupo_restantes = 0
- **THEN** el sistema retorna 409 con mensaje "Cupo agotado para el día seleccionado"
- **AND** no se crea ninguna reserva

#### Scenario: Reservar sin estar en padrón retorna error
- **WHEN** un ALUMNO no incluido en el padrón de la evaluación intenta reservar
- **THEN** el sistema retorna 403 con mensaje "No está habilitado para esta convocatoria"

#### Scenario: Reservar sin permiso coloquios:reservar retorna 403
- **WHEN** un COORDINADOR envía POST /api/coloquios/{id}/reservar
- **THEN** el sistema retorna 403

#### Scenario: Reservar en evaluación inexistente retorna 404
- **WHEN** un ALUMNO intenta reservar en un coloquio con id inexistente
- **THEN** el sistema retorna 404

### Requirement: Alumno cancela reserva
El sistema SHALL exponer un endpoint `PATCH /api/coloquios/reservas/{id}/cancelar` que permita al ALUMNO cancelar su propia reserva. Cambia estado a "Cancelada" y restaura cupo_restantes del día (incrementa en 1).

#### Scenario: Cancelar reserva exitosamente
- **WHEN** un ALUMNO cancela su propia reserva activa
- **THEN** el sistema retorna 200 con estado "Cancelada"
- **AND** cupo_restantes del día se incrementa en 1

#### Scenario: Cancelar reserva de otro alumno retorna 403
- **WHEN** un ALUMNO intenta cancelar una reserva que pertenece a otro alumno
- **THEN** el sistema retorna 403

#### Scenario: Cancelar reserva ya cancelada retorna error
- **WHEN** un ALUMNO intenta cancelar una reserva que ya está en estado "Cancelada"
- **THEN** el sistema retorna 400 con mensaje "La reserva ya está cancelada"

### Requirement: Alumno lista sus reservas
El sistema SHALL exponer un endpoint `GET /api/coloquios/mis-reservas` que retorna las reservas activas del alumno autenticado.

#### Scenario: Listar reservas del alumno
- **WHEN** un ALUMNO consulta GET /api/coloquios/mis-reservas
- **THEN** el sistema retorna 200 con lista de sus reservas activas (evaluacion, día, hora, estado)

#### Scenario: Alumno sin reservas retorna lista vacía
- **WHEN** un ALUMNO sin reservas consulta GET /api/coloquios/mis-reservas
- **THEN** el sistema retorna 200 con lista vacía
