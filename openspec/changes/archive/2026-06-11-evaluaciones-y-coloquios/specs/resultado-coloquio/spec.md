## ADDED Requirements

### Requirement: Registrar nota final de coloquio
El sistema SHALL exponer un endpoint `POST /api/coloquios/{id}/resultados` que permita a COORDINADOR/ADMIN registrar la nota final de un alumno en una evaluación. Recibe `alumno_id` y `nota_final`. Si el alumno ya tiene resultado, lo actualiza.

#### Scenario: Registrar nota final exitosamente
- **WHEN** un COORDINADOR envía POST /api/coloquios/{id}/resultados con alumno_id y nota_final="8"
- **THEN** el sistema retorna 201 con el resultado creado

#### Scenario: Actualizar nota final existente
- **WHEN** un COORDINADOR envía POST /api/coloquios/{id}/resultados para un alumno que ya tiene nota registrada
- **THEN** el sistema retorna 200 con el resultado actualizado

#### Scenario: Registrar nota final sin permiso retorna 403
- **WHEN** un ALUMNO envía POST /api/coloquios/{id}/resultados
- **THEN** el sistema retorna 403

### Requirement: Consultar resultados de una evaluación
El sistema SHALL exponer un endpoint `GET /api/coloquios/{id}/resultados` que retorna todos los resultados registrados para una evaluación, incluyendo datos del alumno (nombre, apellido).

#### Scenario: Consultar resultados exitosamente
- **WHEN** un COORDINADOR consulta GET /api/coloquios/{id}/resultados
- **THEN** el sistema retorna 200 con lista de resultados (alumno_id, nombre, apellido, nota_final)

#### Scenario: Evaluación sin resultados retorna lista vacía
- **WHEN** se consultan resultados de una evaluación sin notas registradas
- **THEN** el sistema retorna 200 con lista vacía

#### Scenario: Consultar resultados sin permiso retorna 403
- **WHEN** un ALUMNO consulta GET /api/coloquios/{id}/resultados
- **THEN** el sistema retorna 403
