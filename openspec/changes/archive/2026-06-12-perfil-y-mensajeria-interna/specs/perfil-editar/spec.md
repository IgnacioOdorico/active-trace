## ADDED Requirements

### Requirement: El sistema SHALL permitir al usuario autenticado ver su propio perfil
El endpoint `GET /api/perfil` devuelve los datos del usuario autenticado (incluyendo PII desencriptada). Requiere permiso `perfil:editar`.

#### Scenario: Ver perfil propio exitosamente
- **WHEN** un usuario autenticado envía `GET /api/perfil`
- **AND** el usuario tiene permiso `perfil:editar`
- **THEN** el sistema retorna `200` con los datos del perfil (nombre, apellidos, email, dni, cuil, cbu, alias_cbu, banco, regional, legajo, legajo_profesional, facturador, estado)

#### Scenario: Ver perfil sin autenticación retorna 401
- **WHEN** un request sin token envía `GET /api/perfil`
- **THEN** el sistema retorna `401`

#### Scenario: Ver perfil sin permiso retorna 403
- **WHEN** un usuario autenticado sin permiso `perfil:editar` envía `GET /api/perfil`
- **THEN** el sistema retorna `403`

### Requirement: El sistema SHALL permitir al usuario autenticado editar su propio perfil
El endpoint `PUT /api/perfil` acepta campos editables del perfil. CUIL no es modificable. Los campos PII se encriptan antes de persistir. Requiere permiso `perfil:editar`.

#### Scenario: Editar perfil exitosamente
- **WHEN** un usuario autenticado envía `PUT /api/perfil` con `{"nombre": "Nuevo", "apellidos": "Apellido", "banco": "Banco Nación", "cbu": "0000000000000000000000"}`
- **AND** el usuario tiene permiso `perfil:editar`
- **THEN** el sistema retorna `200` con los datos actualizados

#### Scenario: Editar perfil con CUIL en el body retorna 422
- **WHEN** un usuario autenticado envía `PUT /api/perfil` incluyendo campo `cuil`
- **THEN** el sistema retorna `422` porque `cuil` no es un campo aceptado en el schema

#### Scenario: Editar perfil sin autenticación retorna 401
- **WHEN** un request sin token envía `PUT /api/perfil`
- **THEN** el sistema retorna `401`

#### Scenario: Editar perfil sin permiso retorna 403
- **WHEN** un usuario autenticado sin permiso `perfil:editar` envía `PUT /api/perfil`
- **THEN** el sistema retorna `403`

#### Scenario: Editar perfil con email duplicado en el tenant retorna 409
- **WHEN** un usuario envía `PUT /api/perfil` con un `email` ya usado por otro usuario en el mismo tenant
- **THEN** el sistema retorna `409` con detalle `EMAIL_DUPLICADO`
