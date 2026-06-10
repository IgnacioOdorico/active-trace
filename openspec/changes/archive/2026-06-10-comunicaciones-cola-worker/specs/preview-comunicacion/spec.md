## ADDED Requirements

### Requirement: Preview de comunicación con variables sustituidas
El sistema SHALL exponer un endpoint que recibe `materia_id`, `destinatario_email`, `asunto_template` y `cuerpo_template`, y retorna el asunto y cuerpo con las variables sustituidas según los datos del destinatario.

#### Scenario: Preview exitoso
- **WHEN** un usuario solicita preview con asunto_template="Aviso para $nombre" y cuerpo_template="Hola $nombre, tu materia $materia..."
- **WHEN** el destinatario existe en el padrón activo de la materia
- **THEN** el sistema retorna asunto y cuerpo con las variables sustituidas por los valores reales

#### Scenario: Preview sin destinatario en padrón
- **WHEN** un usuario solicita preview con un email que no está en el padrón activo
- **THEN** el sistema retorna error 422 con mensaje descriptivo

### Requirement: Preview no modifica estado ni persiste datos
El preview SHALL ser una operación de solo lectura. No SHALL crear registros en la tabla `comunicacion` ni modificar estado alguno.

#### Scenario: Preview es solo lectura
- **WHEN** un usuario solicita preview
- **THEN** no se crean registros en la tabla comunicacion
- **THEN** no se modifican registros existentes
