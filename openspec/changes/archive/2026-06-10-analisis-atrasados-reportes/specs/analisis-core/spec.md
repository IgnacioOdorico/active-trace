## ADDED Requirements

### Requirement: El sistema SHALL computar alumnos atrasados por materia (F2.2, RN-06)
El endpoint `GET /api/analisis/atrasados/{materia_id}` retorna la lista de alumnos que cumplen al menos una condición de atrasado: actividades faltantes (sin calificación registrada) o nota inferior al umbral configurado.

#### Scenario: Alumno sin actividad registrada es atrasado
- **WHEN** un alumno está en el padrón activo de la materia pero no tiene ninguna Calificacion registrada
- **THEN** el sistema lo incluye en la lista de atrasados con motivo "actividades_faltantes"

#### Scenario: Alumno con nota inferior al umbral es atrasado
- **WHEN** un alumno tiene una Calificacion con nota_numerica=40 y el umbral configurado es 60%
- **THEN** el sistema lo incluye en la lista de atrasados con motivo "nota_inferior_umbral"

#### Scenario: Alumno sin ninguna actividad atrasada no aparece
- **WHEN** un alumno tiene todas sus actividades con aprobado=true
- **THEN** el sistema NO lo incluye en la lista de atrasados

#### Scenario: Atrasados usa umbral configurado o defecto 60%
- **WHEN** existe UmbralMateria para la asignación del docente
- **THEN** el sistema usa ese umbral_pct para el cómputo
- **WHEN** no existe UmbralMateria
- **THEN** el sistema usa 60% como valor por defecto

#### Scenario: Atrasados retorna datos del alumno y actividades problemáticas
- **WHEN** se consulta GET /api/analisis/atrasados/{materia_id}
- **THEN** el sistema retorna 200 con lista de alumnos atrasados, cada uno con: nombre, apellidos, email, comisión, lista de actividades problemáticas con motivo

#### Scenario: Sin permiso atrasados:ver retorna 403
- **WHEN** se consulta GET /api/analisis/atrasados/{materia_id} sin permiso `atrasados:ver`
- **THEN** el sistema retorna 403

#### Scenario: Sin padrón activo retorna error claro
- **WHEN** se consulta atrasados para una materia sin padrón activo
- **THEN** el sistema retorna 422 con mensaje "No hay un padrón activo para esta materia"

### Requirement: El sistema SHALL generar ranking de actividades aprobadas (F2.3, RN-09)
El endpoint `GET /api/analisis/ranking/{materia_id}` retorna un ranking descendente de alumnos por cantidad de actividades aprobadas, excluyendo alumnos sin ninguna aprobada.

#### Scenario: Ranking incluye solo alumnos con al menos una aprobada
- **WHEN** se consulta ranking para una materia donde el alumno A tiene 3 aprobadas y el alumno B tiene 0
- **THEN** el alumno A aparece en el ranking con 3 aprobadas
- **AND** el alumno B NO aparece en el ranking

#### Scenario: Ranking ordena descendente por cantidad de aprobadas
- **WHEN** se consulta ranking
- **THEN** los alumnos aparecen ordenados de mayor a menor cantidad de actividades aprobadas

#### Scenario: Ranking retorna datos completos
- **WHEN** se consulta GET /api/analisis/ranking/{materia_id}
- **THEN** el sistema retorna 200 con lista de alumnos y para cada uno: nombre, apellidos, comisión, actividades_aprobadas, total_actividades

#### Scenario: Ranking vacío cuando nadie tiene aprobadas
- **WHEN** ningún alumno tiene actividades aprobadas en la materia
- **THEN** el sistema retorna 200 con lista vacía
