## ADDED Requirements

### Requirement: Crear convocatoria con días y cupos (F7.3)
El sistema SHALL exponer un endpoint `POST /api/coloquios` que permita a COORDINADOR/ADMIN crear una convocatoria de coloquio. El endpoint recibe: materia_id, cohorte_id, tipo, instancia, dias_disponibles (entero), cupo_por_dia (entero). El sistema crea la Evaluacion y genera N registros EvaluacionDia dentro de la ventana definida, cada uno con cupo_maximo = cupo_por_dia y cupos_restantes = cupo_por_dia.

#### Scenario: Crear convocatoria exitosamente
- **WHEN** un COORDINADOR envía POST /api/coloquios con materia_id, cohorte_id, tipo="Coloquio", instancia="Coloquio Final", dias_disponibles=5, cupo_por_dia=10
- **THEN** el sistema retorna 201 con la evaluación creada
- **AND** el sistema crea 5 registros EvaluacionDia con cupo_maximo=10 y cupos_restantes=10

#### Scenario: Crear convocatoria sin permiso retorna 403
- **WHEN** un ALUMNO envía POST /api/coloquios
- **THEN** el sistema retorna 403

#### Scenario: Crear convocatoria con datos inválidos retorna 422
- **WHEN** se envía POST /api/coloquios con dias_disponibles=0 o cupo_por_dia < 1
- **THEN** el sistema retorna 422 con error de validación

### Requirement: Importar alumnos a convocatoria (F7.2)
El sistema SHALL exponer un endpoint `POST /api/coloquios/{id}/alumnos` que recibe una lista de `alumno_id` (UUIDs). Reemplaza TODO el padrón de alumnos habilitados para esa evaluación de forma atómica: elimina los existentes e inserta los nuevos en una sola transacción.

#### Scenario: Importar alumnos exitosamente
- **WHEN** un COORDINADOR envía POST /api/coloquios/{id}/alumnos con lista de 20 alumno_id
- **THEN** el sistema retorna 200 con cantidad de alumnos importados
- **AND** los 20 alumnos quedan habilitados para reservar en esa evaluación

#### Scenario: Importar alumnos reemplaza padrón anterior
- **WHEN** se importan 15 alumnos nuevos a una evaluación que ya tenía 10 alumnos
- **THEN** el sistema reemplaza el padrón: queda con 15 alumnos, los 10 anteriores ya no están habilitados

#### Scenario: Importar alumno inexistente retorna error
- **WHEN** se envía un alumno_id que no existe en Usuario
- **THEN** el sistema retorna 404 con mensaje indicando qué alumno_id no existe

#### Scenario: Importar sin permiso coloquios:gestionar retorna 403
- **WHEN** un ALUMNO envía POST /api/coloquios/{id}/alumnos
- **THEN** el sistema retorna 403
