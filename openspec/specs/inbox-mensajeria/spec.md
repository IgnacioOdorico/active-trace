## ADDED Requirements

### Requirement: El sistema SHALL listar los hilos de mensajes activos del usuario autenticado
El endpoint `GET /api/inbox` devuelve una lista paginada de hilos (mensajes raíz) donde el usuario autenticado es destinatario. Cada hilo muestra el asunto, remitente, fecha del último mensaje, y si tiene mensajes no leídos. Requiere permiso `inbox:leer`.

#### Scenario: Listar inbox exitosamente
- **WHEN** un usuario autenticado con permiso `inbox:leer` envía `GET /api/inbox?pagina=1&page_size=20`
- **THEN** el sistema retorna `200` con una lista paginada de hilos ordenados por fecha descendente

#### Scenario: Listar inbox vacío
- **WHEN** un usuario autenticado sin mensajes envía `GET /api/inbox`
- **THEN** el sistema retorna `200` con `data: []` y `total: 0`

#### Scenario: Listar inbox sin permiso retorna 403
- **WHEN** un usuario autenticado sin permiso `inbox:leer` envía `GET /api/inbox`
- **THEN** el sistema retorna `403`

#### Scenario: Listar inbox con paginación inválida retorna 422
- **WHEN** un usuario envía `GET /api/inbox?pagina=0`
- **THEN** el sistema retorna `422`

### Requirement: El sistema SHALL mostrar un hilo de mensajes completo
El endpoint `GET /api/inbox/{id}` devuelve el mensaje raíz y todas sus respuestas, ordenadas cronológicamente. Requiere permiso `inbox:leer`. Solo el destinatario o el remitente del hilo pueden verlo.

#### Scenario: Ver hilo existente como destinatario
- **WHEN** un usuario autenticado envía `GET /api/inbox/{id}` donde `id` es un hilo donde es destinatario
- **AND** el usuario tiene permiso `inbox:leer`
- **THEN** el sistema retorna `200` con el mensaje raíz y todas las respuestas

#### Scenario: Ver hilo como remitente (reenvío de lectura)
- **WHEN** un usuario autenticado envía `GET /api/inbox/{id}` donde es remitente del hilo (respondió antes)
- **AND** el usuario tiene permiso `inbox:leer`
- **THEN** el sistema retorna `200` con el hilo completo

#### Scenario: Ver hilo inexistente retorna 404
- **WHEN** un usuario autenticado envía `GET /api/inbox/{id}` con un ID que no existe
- **THEN** el sistema retorna `404`

#### Scenario: Ver hilo ajeno retorna 404
- **WHEN** un usuario autenticado envía `GET /api/inbox/{id}` de un hilo donde no es ni remitente ni destinatario
- **THEN** el sistema retorna `404` (no solo 403, para no revelar existencia del hilo)

### Requirement: El sistema SHALL permitir responder dentro de un hilo existente
El endpoint `POST /api/inbox/{id}/responder` agrega un nuevo mensaje al hilo, intercambiando remitente y destinatario respecto al mensaje anterior. Requiere permiso `inbox:responder`.

#### Scenario: Responder a un hilo exitosamente
- **WHEN** un usuario autenticado con permiso `inbox:responder` envía `POST /api/inbox/{id}/responder` con `{"cuerpo": "Mensaje de respuesta"}`
- **AND** el usuario es destinatario del hilo
- **THEN** el sistema retorna `201` con el mensaje creado
- **AND** el remitente original del hilo es ahora el destinatario de la respuesta

#### Scenario: Responder a hilo inexistente retorna 404
- **WHEN** un usuario envía `POST /api/inbox/{id}/responder` con ID de hilo inexistente
- **THEN** el sistema retorna `404`

#### Scenario: Responder a hilo ajeno retorna 404
- **WHEN** un usuario envía `POST /api/inbox/{id}/responder` a un hilo donde no es destinatario
- **THEN** el sistema retorna `404`

#### Scenario: Responder sin permiso retorna 403
- **WHEN** un usuario autenticado sin permiso `inbox:responder` envía `POST /api/inbox/{id}/responder`
- **THEN** el sistema retorna `403`

### Requirement: El sistema SHALL crear un mensaje como notificación del sistema
Un usuario con el rol adecuado (sistema, o vía servicio interno) puede generar un mensaje en el inbox de otro usuario creando un nuevo hilo. Requiere `inbox:leer` en el remitente (el sistema mismo o un actor autorizado).

#### Scenario: Sistema envía notificación a usuario
- **WHEN** un proceso interno del sistema (o un COORDINADOR) genera un mensaje con `remitente_id`, `destinatario_id`, `asunto` y `cuerpo`
- **THEN** se crea un nuevo hilo (thread_id = NULL)
- **AND** el destinatario ve el mensaje en su inbox al listar hilos
