## ADDED Requirements

### Requirement: Endpoint POST /api/comunicaciones/preview
Guarda `comunicacion:enviar`. Recibe `materia_id`, `destinatario_email`, `asunto_template`, `cuerpo_template`. Retorna asunto y cuerpo con variables sustituidas.

#### Scenario: Preview exitoso retorna 200
- **WHEN** se envía POST /api/comunicaciones/preview con datos válidos
- **THEN** sistema retorna 200 con `{ "asunto": "...", "cuerpo": "..." }`

### Requirement: Endpoint POST /api/comunicaciones/enviar
Guarda `comunicacion:enviar`. Recibe `materia_id`, lista de `destinatarios` (emails), `asunto_template`, `cuerpo_template`. Crea una comunicación por cada destinatario con el mismo `lote_id`. Si tenant requiere aprobación → estado `Nueva`→`PendienteAprobacion`. Si no → estado `Nueva`→`Pendiente`.

#### Scenario: Envío masivo sin aprobación
- **WHEN** tenant no requiere aprobación
- **WHEN** se envían 5 destinatarios
- **THEN** se crean 5 comunicaciones con mismo lote_id
- **THEN** todas quedan en estado "Pendiente"
- **THEN** se retorna 201 con lote_id y cantidad

#### Scenario: Envío masivo con aprobación
- **WHEN** tenant requiere aprobación
- **WHEN** se envían 5 destinatarios
- **THEN** todas quedan en estado "PendienteAprobacion"
- **THEN** se retorna 201 con lote_id y cantidad

### Requirement: Endpoint GET /api/comunicaciones
Guarda `comunicacion:enviar`. Retorna comunicaciones paginadas filtrables por `lote_id`, `materia_id`, `estado`. Los destinatarios se retornan descifrados.

#### Scenario: Listar comunicaciones
- **WHEN** se consulta GET /api/comunicaciones?lote_id=X
- **THEN** se retornan las comunicaciones del lote con destinatario descifrado

### Requirement: Endpoint GET /api/comunicaciones/{id}
Guarda `comunicacion:enviar`. Retorna una comunicación por ID con destinatario descifrado.

#### Scenario: Obtener comunicación por ID
- **WHEN** se consulta GET /api/comunicaciones/{id}
- **THEN** se retorna la comunicación con destinatario descifrado
- **WHEN** el id no existe
- **THEN** se retorna 404

### Requirement: Endpoint POST /api/comunicaciones/{id}/cancelar
Guarda `comunicacion:enviar`. Cancela una comunicación individual si está en `Pendiente` o `PendienteAprobacion`.

#### Scenario: Cancelar comunicación Pendiente
- **WHEN** se cancela una comunicación en estado "Pendiente"
- **THEN** la comunicación pasa a "Cancelado"

#### Scenario: Cancelar comunicación ya Enviado falla
- **WHEN** se intenta cancelar una comunicación en estado "Enviado"
- **THEN** se retorna 422 con mensaje de error

### Requirement: Endpoint GET /api/comunicaciones/lotes
Guarda `comunicacion:enviar`. Retorna lista de lotes con metadatos (total, estado counts, fecha primer envío, fecha último).

#### Scenario: Listar lotes
- **WHEN** se consulta GET /api/comunicaciones/lotes
- **THEN** se retorna lista de lotes agrupados con conteo por estado
