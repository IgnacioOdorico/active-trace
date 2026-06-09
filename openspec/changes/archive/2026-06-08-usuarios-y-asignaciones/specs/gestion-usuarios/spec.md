## ADDED Requirements

### Requirement: El sistema SHALL permitir crear usuarios con PII cifrada
El sistema DEBE aceptar nombre, apellidos, email, DNI, CUIL, CBU, alias CBU, banco, regional, legajo, legajo profesional, flag facturador y estado.
El email, DNI, CUIL, CBU y alias CBU DEBEN almacenarse cifrados con AES-256-CBC usando `app/core/security.py`.
El campo `hashed_password` es obligatorio solo para usuarios que se autentican (docentes, coordinadores, admin). Para alumnos puede ser nulo (se genera en C-09).

#### Scenario: Crear usuario con todos los campos PII
- **WHEN** se envía POST /api/admin/usuarios con datos completos (nombre, apellidos, email, DNI, CUIL, CBU, alias, banco, regional, facturador=true, estado=Activo)
- **THEN** el sistema crea el usuario y responde 201 con los datos del usuario
- **AND** los campos email, DNI, CUIL, CBU, alias_cbu aparecen cifrados en la DB (no texto plano)

#### Scenario: Crear usuario sin permisos retorna 403
- **WHEN** se envía POST /api/admin/usuarios sin el permiso `usuarios:gestionar`
- **THEN** el sistema retorna 403 Forbidden

#### Scenario: Crear usuario con email duplicado en el mismo tenant retorna 409
- **WHEN** se envía POST /api/admin/usuarios con un email ya existente en el mismo tenant
- **THEN** el sistema retorna 409 Conflict con código `EMAIL_DUPLICADO`

#### Scenario: Crear usuario con mismo email en distinto tenant es exitoso
- **WHEN** Tenant A crea usuario con email "docente@mail.com"
- **AND** Tenant B crea usuario con mismo email "docente@mail.com"
- **THEN** ambas creaciones son exitosas

### Requirement: El sistema SHALL permitir listar y buscar usuarios
El sistema DEBE exponer GET /api/admin/usuarios con paginación (`page`, `page_size` max 100, `order_by`, `order_dir`).
Debe soportar filtros por: estado, nombre (búsqueda parcial), email (búsqueda exacta, requiere descifrado).

#### Scenario: Listar usuarios con paginación
- **WHEN** se envía GET /api/admin/usuarios?page=1&page_size=10
- **THEN** el sistema retorna 200 con la lista paginada de usuarios
- **AND** la respuesta incluye `data` y `meta` con `total` y `page`

#### Scenario: Filtrar usuarios por estado
- **WHEN** se envía GET /api/admin/usuarios?estado=Activo
- **THEN** el sistema retorna solo usuarios con estado Activo

#### Scenario: Usuario de otro tenant no aparece en listados
- **WHEN** se envía GET /api/admin/usuarios desde Tenant A
- **THEN** ningún usuario de Tenant B aparece en la respuesta

### Requirement: El sistema SHALL permitir actualizar usuarios
El sistema DEBE exponer PATCH /api/admin/usuarios/{id} para modificar campos no sensibles (nombre, banco, regional, legajo, facturador, estado).
Para modificar PII (email, DNI, CUIL, CBU, alias) se requiere re-cifrado.

#### Scenario: Actualizar datos no sensibles
- **WHEN** se envía PATCH /api/admin/usuarios/{id} con campos {banco: "Nuevo Banco"}
- **THEN** el sistema actualiza y retorna 200 con los datos modificados
- **AND** los campos PII no modificados mantienen su cifrado original

#### Scenario: Actualizar email requiere re-cifrado
- **WHEN** se envía PATCH /api/admin/usuarios/{id} con {email: "nuevo@mail.com"}
- **THEN** el nuevo email se almacena cifrado en la DB

#### Scenario: Actualizar usuario inexistente retorna 404
- **WHEN** se envía PATCH /api/admin/usuarios/{uuid-inexistente}
- **THEN** el sistema retorna 404 NotFound

### Requirement: El sistema SHALL permitir activar/desactivar usuarios (soft delete)
El sistema DEBE exponer DELETE /api/admin/usuarios/{id} como soft delete (marca `deleted_at`).

#### Scenario: Soft delete de usuario
- **WHEN** se envía DELETE /api/admin/usuarios/{id}
- **THEN** el sistema marca deleted_at del usuario
- **AND** el usuario no aparece en listados GET
- **AND** el usuario sigue existiendo en la DB (no se elimina físicamente)

### Requirement: El sistema SHALL NO exponer PII en logs ni respuestas de error
Los campos cifrados no deben aparecer en texto plano en ninguna respuesta de la API ni en logs.

#### Scenario: Respuesta de error no incluye PII en texto plano
- **WHEN** ocurre un error al crear/modificar un usuario
- **THEN** la respuesta de error no contiene valores de email, DNI, CUIL, CBU o alias en texto plano
