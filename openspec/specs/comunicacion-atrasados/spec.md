## ADDED Requirements

### Requirement: El sistema SHALL mostrar formulario de redacción con preview inline
El frontend SHALL proveer un formulario donde el profesor redacta asunto y cuerpo con variables, ve un preview con sustitución, y envía a destinatarios seleccionados.

#### Scenario: Redactar y previsualizar comunicación
- **WHEN** el usuario navega a `/comunicaciones` y completa asunto_template, cuerpo_template, selecciona materia y destinatario_email
- **AND** hace clic en "Vista Previa"
- **THEN** el frontend envía POST /api/comunicaciones/preview con materia_id, destinatario_email, asunto_template, cuerpo_template
- **AND** muestra el resultado en un panel de preview: asunto renderizado y cuerpo renderizado con variables sustituidas
- **AND** el preview se marca como "Solo lectura — preview del destinatario seleccionado"

#### Scenario: Preview muestra error si destinatario no existe
- **WHEN** el email del destinatario no está en el padrón activo de la materia
- **THEN** el frontend muestra error "El destinatario no pertenece al padrón de la materia seleccionada"

#### Scenario: Enviar comunicación a múltiples destinatarios
- **WHEN** el usuario selecciona una lista de destinatarios (desde la vista de atrasados o manual)
- **AND** hace clic en "Enviar"
- **THEN** el frontend envía POST /api/comunicaciones/enviar con materia_id, destinatarios[], asunto_template, cuerpo_template
- **AND** muestra mensaje de éxito con lote_id y cantidad de comunicaciones creadas
- **AND** redirige al tracking del lote

### Requirement: El sistema SHALL mostrar tracking del estado de comunicaciones por lote
El frontend SHALL proveer una vista de tracking que muestra el estado de cada comunicación dentro de un lote.

#### Scenario: Tracking muestra lista de comunicaciones del lote
- **WHEN** el usuario es redirigido al tracking post-envío, o navega manualmente
- **THEN** el frontend consulta GET /api/comunicaciones?lote_id=X
- **AND** muestra tabla con columnas: destinatario (email), estado, intentos, error_msg (si hay), enviado_at
- **AND** colorea cada fila según estado (verde=Enviado, amarillo=Pendiente, rojo=Error, gris=Cancelado)

#### Scenario: Tracking con filtros de estado
- **WHEN** el usuario selecciona un filtro de estado (ej. "Solo errores")
- **THEN** la tabla se filtra para mostrar solo comunicaciones con ese estado

#### Scenario: Lote requiere aprobación
- **WHEN** el tenant requiere aprobación de comunicaciones
- **THEN** el frontend muestra indicación "Este lote requiere aprobación antes de ser enviado" con el estado "PendienteAprobacion" visible
- **AND** si el usuario tiene permiso `comunicacion:aprobar`, muestra botones "Aprobar Lote" y "Rechazar Lote"
