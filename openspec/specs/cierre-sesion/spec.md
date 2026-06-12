## ADDED Requirements

### Requirement: El sistema SHALL permitir al usuario cerrar sesión explícitamente
Se reutiliza el endpoint `POST /api/auth/logout` existente (implementado en C-03) que invalida el refresh token activo del usuario.

#### Scenario: Cerrar sesión exitosamente
- **WHEN** un usuario autenticado envía `POST /api/auth/logout` con su refresh token
- **THEN** el sistema retorna `200` y el refresh token queda invalidado

#### Scenario: Cerrar sesión sin autenticación
- **WHEN** un request sin token envía `POST /api/auth/logout`
- **THEN** el sistema retorna `401`
