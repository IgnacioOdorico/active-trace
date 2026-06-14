## ADDED Requirements

### Requirement: El sistema SHALL proveer monitor general de actividades (F2.7)
El endpoint `GET /api/analisis/monitor-general` retorna una vista transversal paginada de todos los alumnos del tenant con su estado de actividades, filtrable por materia, regional, comisión, búsqueda por alumno y estado de actividad.

#### Scenario: Monitor general retorna alumnos paginados con estado
- **WHEN** se consulta GET /api/analisis/monitor-general sin filtros
- **THEN** el sistema retorna 200 con lista paginada de alumnos, cada uno con: nombre, apellidos, email, comisión, regional, materia, total_actividades, aprobadas, estado (atrasado/al_dia)

#### Scenario: Monitor general filtra por materia
- **WHEN** se consulta con materia_id
- **THEN** el sistema filtra solo alumnos de esa materia

#### Scenario: Monitor general filtra por regional
- **WHEN** se consulta con regional="CABA"
- **THEN** el sistema filtra solo alumnos de esa regional

#### Scenario: Monitor general filtra por comisión
- **WHEN** se consulta con comision="A"
- **THEN** el sistema filtra solo alumnos de esa comisión

#### Scenario: Monitor general permite búsqueda por nombre de alumno
- **WHEN** se consulta con q="Juan"
- **THEN** el sistema filtra alumnos cuyo nombre o apellidos contengan "Juan" (case-insensitive)

#### Scenario: Monitor general filtra por estado de actividad
- **WHEN** se consulta con estado="atrasado"
- **THEN** el sistema retorna solo alumnos atrasados
- **WHEN** se consulta con estado="al_dia"
- **THEN** el sistema retorna solo alumnos al día

#### Scenario: Monitor general paginado
- **WHEN** se consulta con pagina=2 y por_pagina=50
- **THEN** el sistema retorna la página 2 con hasta 50 resultados
- **AND** retorna total de resultados para calcular páginas

### Requirement: El sistema SHALL proveer monitor de seguimiento para tutor/profesor (F2.8)
El endpoint `GET /api/analisis/monitor-seguimiento` retorna una vista filtrable del estado de actividades de los alumnos asignados al usuario que consulta.

#### Scenario: Monitor seguimiento filtra por alumno específico
- **WHEN** un tutor consulta con alumno_id
- **THEN** el sistema retorna las actividades de ese alumno en las materias del tutor

#### Scenario: Monitor seguimiento filtra por comisión
- **WHEN** un profesor consulta con comision="A"
- **THEN** el sistema retorna alumnos de esa comisión en sus materias

#### Scenario: Monitor seguimiento muestra mínimo de actividad cumplida
- **WHEN** se consulta con actividad_minima="TP1"
- **THEN** el sistema filtra alumnos que tienen registrada esa actividad

### Requirement: El sistema SHALL extender monitor de seguimiento con rango de fechas (F2.9)
El endpoint `GET /api/analisis/monitor-seguimiento` acepta filtros adicionales de rango de fechas cuando el usuario tiene permiso de coordinación/admin.

#### Scenario: Monitor seguimiento con rango de fechas
- **WHEN** un coordinador consulta con desde=2026-03-01 y hasta=2026-06-01
- **THEN** el sistema acota el análisis a calificaciones dentro de ese rango de importado_at

#### Scenario: Monitor seguimiento sin rango de fechas usa todo el período
- **WHEN** un tutor consulta sin desde/hasta
- **THEN** el sistema analiza todas las calificaciones disponibles

#### Scenario: Monitor seguimiento scope por asignación del usuario
- **WHEN** un profesor consulta el monitor
- **THEN** el sistema solo retorna datos de las materias donde tiene asignación activa
- **WHEN** un coordinador consulta
- **THEN** el sistema retorna datos de todas las materias del tenant (scope global)
