## ADDED Requirements

### Requirement: ABM de avisos
El sistema SHALL exponer endpoints CRUD para gestionar avisos, protegidos por el permiso `avisos:publicar` (COORDINADOR, ADMIN).

#### Scenario: Crear aviso
- **WHEN** un COORDINADOR envía POST /api/avisos con datos válidos (alcance, título, cuerpo, inicio_en, fin_en, severidad, orden)
- **THEN** el sistema crea el aviso y retorna el id
- **THEN** el sistema registra audit log con accion="AVISO_PUBLICAR"

#### Scenario: Crear aviso sin permiso
- **WHEN** un ALUMNO intenta crear un aviso
- **THEN** el sistema retorna 403

#### Scenario: Editar aviso
- **WHEN** un COORDINADOR edita un aviso existente
- **THEN** el sistema persiste los cambios
- **THEN** updated_at se actualiza
- **THEN** el sistema registra audit log con accion="AVISO_EDITAR"

#### Scenario: Editar aviso inexistente
- **WHEN** un usuario intenta editar un aviso con ID inexistente
- **THEN** el sistema retorna 404

#### Scenario: Eliminar aviso (soft delete)
- **WHEN** un COORDINADOR elimina un aviso
- **THEN** el sistema marca deleted_at (soft delete)
- **THEN** el sistema registra audit log con accion="AVISO_ELIMINAR"
- **THEN** el aviso deja de aparecer en listados

#### Scenario: Listar avisos (gestión)
- **WHEN** un COORDINADOR lista todos los avisos del tenant
- **THEN** el sistema retorna avisos paginados (incluyendo no activos y fuera de vigencia)
- **THEN** cada aviso incluye metadatos de gestión (activo, contador de acknowledgments)
