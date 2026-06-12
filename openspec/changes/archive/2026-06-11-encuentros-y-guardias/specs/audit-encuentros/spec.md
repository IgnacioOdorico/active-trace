## ADDED Requirements

### Requirement: Registro de auditoría para encuentros
El sistema SHALL registrar en el audit log las acciones de creación y edición de encuentros con el código `ENCUENTRO_CREAR` y `ENCUENTRO_EDITAR` respectivamente.

#### Scenario: Auditoría al crear slot recurrente
- **WHEN** un usuario crea un SlotEncuentro con cant_semanas > 0
- **THEN** el sistema registra un audit log con accion="ENCUENTRO_CREAR"
- **THEN** el detalle incluye slot_id y cantidad de instancias generadas

#### Scenario: Auditoría al crear encuentro único
- **WHEN** un usuario crea una InstanciaEncuentro sin slot padre
- **THEN** el sistema registra un audit log con accion="ENCUENTRO_CREAR"
- **THEN** el detalle incluye instancia_id

#### Scenario: Auditoría al editar instancia
- **WHEN** un usuario modifica el estado de una InstanciaEncuentro
- **THEN** el sistema registra un audit log con accion="ENCUENTRO_EDITAR"
- **THEN** el detalle incluye instancia_id, estado anterior y estado nuevo

### Requirement: Registro de auditoría para guardias
El sistema SHALL registrar en el audit log la creación de guardias con el código `GUARDIA_CREAR`.

#### Scenario: Auditoría al crear guardia
- **WHEN** un tutor registra una guardia
- **THEN** el sistema registra un audit log con accion="GUARDIA_CREAR"
- **THEN** el detalle incluye guardia_id, materia_id y asignacion_id
