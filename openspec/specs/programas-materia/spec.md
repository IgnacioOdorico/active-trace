## ADDED Requirements

### Requirement: ABM de programas de materia
El sistema SHALL exponer endpoints CRUD para gestionar programas de materia, protegidos por el permiso `estructura:gestionar`.

#### Scenario: Crear programa
- **WHEN** un COORDINADOR envía POST /api/programas con materia_id, carrera_id, cohorte_id, titulo y referencia_archivo
- **THEN** el sistema crea el programa y retorna el id

#### Scenario: Listar programas por materia
- **WHEN** un COORDINADOR lista programas filtrados por materia_id
- **THEN** el sistema retorna los programas de esa materia

#### Scenario: Editar programa
- **WHEN** un COORDINADOR edita el titulo o referencia_archivo de un programa
- **THEN** el sistema persiste los cambios

#### Scenario: Eliminar programa
- **WHEN** un COORDINADOR elimina un programa
- **THEN** el sistema marca soft delete
