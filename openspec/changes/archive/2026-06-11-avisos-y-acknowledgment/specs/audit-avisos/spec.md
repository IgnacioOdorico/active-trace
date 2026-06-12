## ADDED Requirements

### Requirement: Registro de auditoría para avisos
El sistema SHALL registrar en el audit log las acciones de creación, edición y eliminación de avisos con los códigos `AVISO_PUBLICAR`, `AVISO_EDITAR` y `AVISO_ELIMINAR` respectivamente.

#### Scenario: Auditoría al crear aviso
- **WHEN** un COORDINADOR crea un aviso
- **THEN** el sistema registra un audit log con accion="AVISO_PUBLICAR"
- **THEN** el detalle incluye aviso_id y título

#### Scenario: Auditoría al editar aviso
- **WHEN** un COORDINADOR edita un aviso existente
- **THEN** el sistema registra un audit log con accion="AVISO_EDITAR"
- **THEN** el detalle incluye aviso_id y campos modificados

#### Scenario: Auditoría al eliminar aviso
- **WHEN** un COORDINADOR elimina un aviso
- **THEN** el sistema registra un audit log con accion="AVISO_ELIMINAR"
- **THEN** el detalle incluye aviso_id y título
