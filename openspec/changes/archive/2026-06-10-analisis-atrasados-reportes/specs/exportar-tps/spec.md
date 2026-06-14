## ADDED Requirements

### Requirement: El sistema SHALL exportar TPs sin corregir a archivo descargable (F2.6, RN-07/08)
El endpoint `GET /api/analisis/exportar-tps/{materia_id}` genera un archivo .xlsx con el listado de entregas textuales detectadas como pendientes de corrección.

#### Scenario: Export genera xlsx con entregas sin calificar
- **WHEN** se consulta GET /api/analisis/exportar-tps/{materia_id} y existen entregas textuales sin calificación
- **THEN** el sistema genera un archivo .xlsx con columnas: Alumno, Actividad, Estado
- **AND** retorna 200 con Content-Type application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

#### Scenario: Export sin entregas retorna mensaje informativo
- **WHEN** se consulta exportar-tps y no hay entregas sin calificar
- **THEN** el sistema retorna 200 con JSON `{"total": 0, "mensaje": "No se encontraron entregas sin corregir"}`

#### Scenario: Export incluye solo actividades textuales (RN-08)
- **WHEN** se genera el export
- **THEN** solo se incluyen actividades de tipo textual (cualitativa)
- **AND** actividades numéricas sin nota NO se incluyen

#### Scenario: Export cruza reporte de finalización con calificaciones (RN-07)
- **WHEN** se genera el export
- **THEN** el sistema cruza el reporte de finalización del LMS contra calificaciones importadas
- **AND** solo incluye entregas "Entregado"/"Enviado"/"Submitted" sin calificación registrada

#### Scenario: Export sin permiso retorna 403
- **WHEN** se consulta GET /api/analisis/exportar-tps/{materia_id} sin permiso `atrasados:ver`
- **THEN** el sistema retorna 403

### Requirement: El sistema SHALL permitir subir reporte de finalización para export
El endpoint acepta un archivo de finalización opcional como query parameter `reporte_url` o sube un archivo para cruzar contra calificaciones existentes.

#### Scenario: Export con archivo de finalización opcional
- **WHEN** se provee un archivo de reporte de finalización
- **THEN** el sistema cruza ese reporte contra las calificaciones de la materia
- **WHEN** no se provee archivo
- **THEN** el sistema usa las calificaciones textuales sin nota como base del export
