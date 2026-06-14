## ADDED Requirements

### Requirement: Worker procesa comunicaciones Pendiente → Enviado
El worker SHALL ejecutar un loop infinito que cada N segundos (configurable vía `WORKER_POLL_INTERVAL`, default 10s):
1. Consulta comunicaciones con `estado='Pendiente'` (ordenadas por `created_at ASC`, limit 50)
2. Para cada una: actualiza a `estado='Enviando'` con `UPDATE ... WHERE estado='Pendiente' RETURNING *` (optimistic lock)
3. Ejecuta el envío (mock/stub que simula SMTP)
4. Si éxito: `estado='Enviado'`, `enviado_at=now()`
5. Si error: incrementa `intentos`. Si `intentos < 3`: `estado='Pendiente'`. Si `intentos >= 3`: `estado='Error'`, `error_msg=desc`

#### Scenario: Worker procesa comunicación exitosamente
- **WHEN** el worker encuentra una comunicación Pendiente
- **THEN** la cambia a "Enviando" atómicamente
- **WHEN** el envío simulado es exitoso
- **THEN** la comunicación queda en "Enviado" con enviado_at no nulo

#### Scenario: Worker reintenta hasta 3 veces
- **WHEN** el worker encuentra una comunicación Pendiente
- **WHEN** el envío simulado falla las primeras 2 veces
- **THEN** después del 1er y 2do error, la comunicación vuelve a "Pendiente" con intentos incrementados
- **WHEN** el 3er intento también falla
- **THEN** la comunicación queda en "Error" con error_msg del último fallo

#### Scenario: Worker no toma comunicación ya en Enviando
- **WHEN** dos workers ejecutan simultáneamente
- **WHEN** el primero cambia Pendiente → Enviando
- **THEN** el segundo worker no encuentra esa comunicación en Pendiente y la salta

### Requirement: Plantillas con variables de sustitución
El sistema SHALL usar `string.Template` de Python stdlib para las plantillas. Variables disponibles: `$nombre`, `$materia`, `$comision`, `$asunto`.

#### Scenario: Sustitución de variables en plantilla
- **WHEN** la plantilla es "Hola $nombre, tu materia $materia tiene actividades pendientes"
- **WHEN** los valores son nombre="Juan", materia="Programación I"
- **THEN** el resultado es "Hola Juan, tu materia Programación I tiene actividades pendientes"

### Requirement: Worker registra audit log por comunicación enviada
El worker SHALL registrar un audit log con código `COMUNICACION_ENVIAR` por cada comunicación que transiciona a "Enviado", incluyendo `lote_id` en el detalle.

#### Scenario: Audit log por envío exitoso
- **WHEN** el worker cambia una comunicación a "Enviado"
- **THEN** se crea un AuditLog con accion="COMUNICACION_ENVIAR", filas_afectadas=1, detalle incluyendo lote_id y comunicación id

### Requirement: Worker graceful shutdown
El worker SHALL manejar `asyncio.CancelledError` y `SIGTERM` para terminar el loop ordenadamente, esperando que la comunicación en curso termine antes de salir.

#### Scenario: Shutdown ordenado
- **WHEN** se envía SIGTERM al worker
- **THEN** el worker termina el procesamiento de la comunicación actual
- **THEN** el worker sale sin corrupción de datos
