## ADDED Requirements

### Requirement: El sistema SHALL mostrar vista de importación con wizard de 2 pasos
El frontend SHALL implementar un flujo wizard de 2 pasos: Paso 1 (subir archivo + preview) y Paso 2 (seleccionar actividades + confirmar).

#### Scenario: Paso 1 muestra formulario de carga y tabla de preview
- **WHEN** el usuario navega a `/calificaciones/importar` y selecciona un archivo .xlsx/.csv y una materia
- **AND** hace clic en "Vista Previa"
- **THEN** el frontend envía POST /api/calificaciones/preview con el archivo y materia_id
- **AND** muestra la tabla de preview con actividades detectadas, tipo (numérica/textual), columnas de identificación de alumnos y primeras filas de datos
- **AND** permite seleccionar/deseleccionar actividades mediante checkboxes

#### Scenario: Paso 2 confirma importación con actividades seleccionadas
- **WHEN** el usuario selecciona una o más actividades en la tabla de preview
- **AND** hace clic en "Importar Seleccionadas"
- **THEN** el frontend envía POST /api/calificaciones/importar con materia_id y lista de actividades seleccionadas
- **AND** muestra resumen con cantidad de calificaciones insertadas, actualizadas, y advertencias por fila

#### Scenario: Error en preview muestra mensaje descriptivo
- **WHEN** el archivo no tiene actividades detectables o tiene formato inválido
- **THEN** el frontend muestra el mensaje de error retornado por la API (ej. "No se detectaron actividades evaluables")

#### Scenario: Indicador de carga durante la subida
- **WHEN** el archivo se está subiendo para preview
- **THEN** el frontend muestra un spinner/barra de progreso y deshabilita el botón de "Vista Previa"

### Requirement: El sistema SHALL mostrar resultado detallado post-importación
Después de una importación exitosa, el frontend SHALL mostrar un resumen visual con insertadas, actualizadas y advertencias.

#### Scenario: Resumen muestra conteos y advertencias expandibles
- **WHEN** la importación finaliza con insertadas=50, actualizadas=3, advertencias=2
- **THEN** el frontend muestra un banner verde con "50 calificaciones insertadas, 3 actualizadas"
- **AND** muestra las advertencias como una lista expandible con detalle de fila y motivo

#### Scenario: Error de permiso redirige o muestra acceso denegado
- **WHEN** el usuario no tiene permiso `calificaciones:importar`
- **THEN** el frontend muestra mensaje "No tiene permisos para importar calificaciones"
- **AND** el sidebar oculta la entrada si el permiso falta
