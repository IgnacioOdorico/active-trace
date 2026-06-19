## ADDED Requirements

### Requirement: El sistema SHALL mostrar dashboard con métricas rápidas de la materia
El frontend SHALL proveer una vista tipo dashboard con tarjetas de métricas consolidadas para la materia seleccionada.

#### Scenario: Dashboard carga métricas al seleccionar materia
- **WHEN** el usuario navega a `/reportes` y selecciona una materia
- **THEN** el frontend consulta GET /api/analisis/reportes/{materia_id}
- **AND** muestra tarjetas con: total_alumnos, total_actividades, total_calificaciones, promedio_aprobacion_general, alumnos_atrasados_count, alumnos_aprobados_count

#### Scenario: Dashboard sin datos muestra indicador
- **WHEN** la materia no tiene calificaciones importadas (sin_datos: true)
- **THEN** el frontend muestra un mensaje "No hay datos de calificaciones para esta materia"
- **AND** sugiere ir a importar calificaciones con un enlace a `/calificaciones/importar`

### Requirement: El sistema SHALL permitir calcular nota final promedio seleccionando actividades
El frontend SHALL proveer un selector de actividades y una tabla de resultados de nota final por alumno.

#### Scenario: Seleccionar actividades y calcular nota final
- **WHEN** el usuario selecciona una o más actividades numéricas de la lista disponible
- **AND** hace clic en "Calcular Nota Final"
- **THEN** el frontend envía POST /api/analisis/notas-finales con materia_id y lista de actividades seleccionadas
- **AND** muestra tabla con columnas: nombre, apellidos, comisión, nota_final (promedio), actividades_textuales (si aplica), estado (aprobado/no aprobado según umbral)
- **AND** permite descargar los resultados como CSV

#### Scenario: Actividades textuales se identifican visualmente
- **WHEN** la lista de actividades disponibles incluye actividades textuales
- **THEN** se muestran con un badge/indicador "Textual" y están excluidas del cálculo de nota final
- **AND** un tooltip explica "Las actividades textuales no se incluyen en el promedio numérico"
