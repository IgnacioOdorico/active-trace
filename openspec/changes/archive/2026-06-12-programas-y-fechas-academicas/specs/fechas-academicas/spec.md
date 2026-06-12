## ADDED Requirements

### Requirement: CRUD de fechas académicas
El sistema SHALL exponer endpoints CRUD para gestionar fechas de evaluación, protegidos por el permiso `estructura:gestionar`.

#### Scenario: Crear fecha académica
- **WHEN** un COORDINADOR crea una fecha académica con materia_id, cohorte_id, tipo, numero, periodo, fecha y titulo
- **THEN** el sistema persiste la fecha

#### Scenario: Listar fechas por materia y cohorte
- **WHEN** un COORDINADOR lista fechas filtradas por materia_id y cohorte_id
- **THEN** el sistema retorna las fechas ordenadas por fecha ascendente

#### Scenario: Generar fragmento LMS
- **WHEN** un COORDINADOR solicita el fragmento LMS para una materia y cohorte
- **THEN** el sistema retorna un string HTML con las fechas en formato tabla
