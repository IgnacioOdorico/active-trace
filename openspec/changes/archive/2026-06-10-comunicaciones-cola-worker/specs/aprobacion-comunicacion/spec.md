## ADDED Requirements

### Requirement: Aprobación de comunicaciones por lote
El sistema SHALL permitir que un usuario con permiso `comunicacion:aprobar` apruebe todas las comunicaciones de un `lote_id` que estén en estado `PendienteAprobacion`, transicionándolas a `Pendiente`.

#### Scenario: Aprobar lote completo
- **WHEN** un usuario con permiso `comunicacion:aprobar` aprueba el lote_id X
- **THEN** todas las comunicaciones del lote en estado "PendienteAprobacion" pasan a "Pendiente"
- **THEN** las que ya están en otro estado no se modifican

### Requirement: Rechazo de comunicaciones por lote
El sistema SHALL permitir que un usuario con permiso `comunicacion:aprobar` rechace (cancele) todas las comunicaciones de un `lote_id` en estado `PendienteAprobacion`, transicionándolas a `Cancelado`.

#### Scenario: Rechazar lote completo
- **WHEN** un usuario con permiso `comunicacion:aprobar` rechaza el lote_id X
- **THEN** todas las comunicaciones del lote en estado "PendienteAprobacion" pasan a "Cancelado"

### Requirement: Aprobación individual de comunicación
El sistema SHALL permitir aprobar o rechazar comunicaciones individualmente (por `id`) además de por lote.

#### Scenario: Aprobar comunicación individual
- **WHEN** un usuario con permiso `comunicacion:aprobar` aprueba la comunicación id Y
- **THEN** si la comunicación está en "PendienteAprobacion", pasa a "Pendiente"
- **THEN** si la comunicación está en otro estado, se retorna error 422

### Requirement: Guard de permiso comunicacion:aprobar
El sistema SHALL proteger los endpoints de aprobación/rechazo con el permiso `comunicacion:aprobar`. Usuarios sin este permiso SHALL recibir 403.

#### Scenario: Acceso denegado sin permiso
- **WHEN** un usuario sin permiso `comunicacion:aprobar` intenta aprobar un lote
- **THEN** el sistema retorna 403 Forbidden
