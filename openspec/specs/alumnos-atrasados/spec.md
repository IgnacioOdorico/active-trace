## ADDED Requirements

### Requirement: El sistema SHALL mostrar ranking de alumnos atrasados
El frontend SHALL proveer una vista de alumnos atrasados ordenada por cantidad de actividades no aprobadas (descendente), filtrable por materia.

#### Scenario: Vista inicial carga ranking de atrasados
- **WHEN** el usuario navega a `/alumnos/atrasados`
- **THEN** el frontend consulta GET /api/analisis/atrasados con filtros por defecto (materia del usuario si tiene una sola)
- **AND** muestra tabla con columnas: nombre, apellidos, email, comisión, actividades_no_aprobadas, total_actividades, progreso (porcentaje), última_actividad
- **AND** ordena por actividades_no_aprobadas descendente (más atrasados primero)

#### Scenario: Filtrar ranking por materia
- **WHEN** el usuario selecciona una materia del selector
- **THEN** el frontend actualiza la consulta GET /api/analisis/atrasados?materia_id=X
- **AND** refresca la tabla con los datos filtrados

#### Scenario: Cada fila tiene acción rápida "Comunicar"
- **WHEN** el usuario hace clic en "Comunicar" en una fila
- **THEN** el frontend navega a `/comunicaciones` con el email del alumno preseleccionado como destinatario
- **AND** mantiene la materia seleccionada como contexto

#### Scenario: Indicador visual de gravedad
- **WHEN** un alumno tiene más del 50% de actividades no aprobadas
- **THEN** la fila se muestra con un indicador visual (color/icono) de "Crítico"
- **WHEN** tiene entre 25% y 50%
- **THEN** la fila se muestra con indicador de "Atención"
- **WHEN** tiene menos del 25%
- **THEN** la fila se muestra con indicador de "Seguimiento"

#### Scenario: Paginación en ranking
- **WHEN** hay más de 50 alumnos atrasados
- **THEN** la tabla muestra controles de paginación (anterior/siguiente/número de página)
