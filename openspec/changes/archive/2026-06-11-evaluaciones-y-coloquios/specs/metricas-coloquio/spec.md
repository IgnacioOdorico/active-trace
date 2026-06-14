## ADDED Requirements

### Requirement: Panel de métricas de coloquios (F7.1)
El sistema SHALL exponer un endpoint `GET /api/coloquios/metricas` que retorna métricas globales del tenant: total de alumnos cargados en padrones de evaluaciones activas, total de instancias activas (evaluaciones con al menos un día en el futuro), total de reservas activas, total de notas registradas.

#### Scenario: Obtener métricas exitosamente
- **WHEN** un COORDINADOR consulta GET /api/coloquios/metricas
- **THEN** el sistema retorna 200 con: total_alumnos_convocados (entero), total_instancias_activas (entero), total_reservas_activas (entero), total_notas_registradas (entero)

#### Scenario: Métricas sin datos retornan ceros
- **WHEN** no hay evaluaciones creadas
- **THEN** el sistema retorna 200 con todos los valores en 0

#### Scenario: Métricas sin permiso coloquios:gestionar retorna 403
- **WHEN** un ALUMNO consulta GET /api/coloquios/metricas
- **THEN** el sistema retorna 403

### Requirement: Métricas por convocatoria individual
El sistema SHALL exponer un endpoint `GET /api/coloquios/{id}/metricas` que retorna métricas específicas de una convocatoria: total de alumnos convocados, total de reservas activas, total de cupos libres (suma de cupos_restantes de todos los días), total de notas registradas.

#### Scenario: Obtener métricas de convocatoria
- **WHEN** un COORDINADOR consulta GET /api/coloquios/{id}/metricas
- **THEN** el sistema retorna 200 con: convocados, reservas_activas, cupos_libres, notas_registradas

#### Scenario: Convocatoria sin alumnos retorna métricas en cero
- **WHEN** se consultan métricas de una convocatoria sin padrón cargado
- **THEN** el sistema retorna 200 con convocados=0, reservas_activas=0, cupos_libres igual a suma de cupo_maximo, notas_registradas=0
