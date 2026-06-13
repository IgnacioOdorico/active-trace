## ADDED Requirements

### Requirement: El sistema SHALL mostrar monitor general de actividades
El frontend SHALL proveer una vista paginada del estado de actividades de todos los alumnos, con múltiples filtros.

#### Scenario: Monitor general carga con paginación
- **WHEN** el usuario navega a `/monitores`
- **THEN** el frontend consulta GET /api/analisis/monitor-general con página inicial 1
- **AND** muestra tabla paginada con columnas: nombre, apellidos, email, comisión, regional, materia, total_actividades, aprobadas, estado (atrasado/al_dia)
- **AND** colorea cada fila según estado (rojo=atrasado, verde=al_dia)

#### Scenario: Filtrar monitor por materia, comisión, regional
- **WHEN** el usuario selecciona una materia, comisión o regional en los filtros
- **THEN** el frontend actualiza la consulta GET /api/analisis/monitor-general con los filtros seleccionados
- **AND** refresca la tabla

#### Scenario: Búsqueda por nombre de alumno
- **WHEN** el usuario escribe "Juan" en el campo de búsqueda
- **THEN** el frontend consulta GET /api/analisis/monitor-general?q=Juan
- **AND** la tabla muestra solo alumnos cuyo nombre/apellidos contienen "Juan"

#### Scenario: Filtrar por estado de actividad
- **WHEN** el usuario selecciona filtro estado="atrasado"
- **THEN** el frontend consulta GET /api/analisis/monitor-general?estado=atrasado
- **AND** la tabla muestra solo alumnos atrasados

### Requirement: El sistema SHALL mostrar monitor de seguimiento con scope según rol
El frontend SHALL adaptar la vista de seguimiento según el rol del usuario (profesor ve sus materias, coordinador ve todo).

#### Scenario: Monitor seguimiento carga según rol
- **WHEN** el usuario navega a la pestaña "Seguimiento" dentro de `/monitores`
- **THEN** el frontend consulta GET /api/analisis/monitor-seguimiento
- **AND** si el usuario es profesor, muestra solo alumnos de sus materias asignadas
- **AND** si el usuario es coordinador, muestra selector de materia para filtrar

#### Scenario: Filtrar seguimiento por alumno específico
- **WHEN** el usuario selecciona un alumno del selector (o escribe su nombre)
- **THEN** el frontend consulta GET /api/analisis/monitor-seguimiento?alumno_id=UUID
- **AND** muestra las actividades de ese alumno con sus calificaciones

#### Scenario: Filtrar seguimiento por actividad mínima
- **WHEN** el usuario selecciona "TP1" como actividad mínima
- **THEN** el frontend consulta GET /api/analisis/monitor-seguimiento?actividad_minima=TP1
- **AND** la tabla filtra alumnos que tienen registrada esa actividad

#### Scenario: Rango de fechas visible solo para coordinadores
- **WHEN** el usuario es coordinador
- **THEN** el frontend muestra campos de fecha "Desde" y "Hasta" en los filtros
- **WHEN** el usuario es profesor/tutor
- **THEN** los campos de rango de fechas no se muestran

#### Scenario: Paginación en ambos monitores
- **WHEN** hay más de 50 resultados
- **THEN** ambas tablas (general y seguimiento) muestran controles de paginación con total de resultados
