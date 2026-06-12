## ADDED Requirements

### Requirement: Confirmar lectura de aviso (acknowledgment)
El sistema SHALL permitir a un usuario confirmar la lectura de un aviso mediante POST /api/avisos/{id}/ack. La operación es idempotente.

#### Scenario: Confirmar lectura exitosamente
- **WHEN** un usuario envía POST /api/avisos/{id}/ack para un aviso visible
- **THEN** el sistema crea un registro en AcknowledgmentAviso con la fecha/hora actual
- **THEN** retorna éxito

#### Scenario: Confirmar lectura de aviso ya confirmado (idempotencia)
- **WHEN** un usuario envía POST /api/avisos/{id}/ack para un aviso que ya confirmó
- **THEN** el sistema retorna éxito sin crear duplicado
- **THEN** no hay error ni duplicación

#### Scenario: Confirmar lectura de aviso inexistente
- **WHEN** un usuario intenta confirmar un aviso con ID inexistente
- **THEN** el sistema retorna 404

### Requirement: Contadores de acknowledgment
El sistema SHALL exponer contadores derivados desde la tabla AcknowledgmentAviso, no denormalizados.

#### Scenario: Contador de confirmaciones
- **WHEN** un COORDINADOR consulta el detalle de un aviso
- **THEN** el sistema retorna total_acks = COUNT de AcknowledgmentAviso para ese aviso
