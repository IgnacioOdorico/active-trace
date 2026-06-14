## ADDED Requirements

### Requirement: Auditar creación de comunicaciones
El sistema SHALL registrar un AuditLog con acción `COMUNICACION_ENVIAR` al crear un lote de comunicaciones, incluyendo cantidad de destinatarios y lote_id.

#### Scenario: Audit log al encolar lote
- **WHEN** un usuario envía un lote de 10 comunicaciones
- **THEN** se registra un AuditLog con accion="COMUNICACION_ENVIAR", filas_afectadas=10, detalle incluyendo lote_id

### Requirement: Auditar aprobación/rechazo de lote
El sistema SHALL registrar un AuditLog con acción `COMUNICACION_ENVIAR` y detalle indicando "aprobado" o "rechazado" cuando un aprobador procesa un lote.

#### Scenario: Audit log al aprobar lote
- **WHEN** un usuario con permiso `comunicacion:aprobar` aprueba un lote
- **THEN** se registra un AuditLog con accion="COMUNICACION_ENVIAR", detalle incluyendo lote_id y "aprobado: true"

### Requirement: No auditar cambios de estado internos del worker
El worker NO SHALL generar audit logs individuales por cada cambio de estado interno (Pendiente → Enviando). Solo SHALL auditar cuando la comunicación llega a estado final (Enviado o Error).

#### Scenario: Sin audit por cambio interno
- **WHEN** el worker cambia Pendiente → Enviando
- **THEN** NO se registra audit log

#### Scenario: Audit por comunicación enviada
- **WHEN** el worker cambia Enviando → Enviado
- **THEN** se registra audit log con accion="COMUNICACION_ENVIAR"
