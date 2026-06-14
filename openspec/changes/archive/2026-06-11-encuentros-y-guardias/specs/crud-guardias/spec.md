## ADDED Requirements

### Requirement: CRUD de guardias para tutores
El sistema SHALL permitir a un TUTOR registrar, listar y editar sus propias guardias. La consulta global (todas las guardias del tenant) está disponible para COORDINADOR y ADMIN.

#### Scenario: Tutor registra guardia
- **WHEN** un tutor envía POST /api/guardias con datos válidos
- **THEN** el sistema crea la guardia con estado "Pendiente"
- **THEN** la respuesta incluye el id de la guardia creada

#### Scenario: Tutor lista sus guardias
- **WHEN** un tutor consulta GET /api/guardias
- **THEN** el sistema retorna las guardias asociadas a sus asignaciones
- **THEN** la respuesta incluye meta con total y página

#### Scenario: Tutor edita guardia propia
- **WHEN** un tutor modifica el estado de una guardia que le pertenece
- **THEN** el sistema persiste el cambio

#### Scenario: Tutor no puede editar guardia de otro
- **WHEN** un tutor intenta modificar una guardia de otro tutor
- **THEN** el sistema retorna 404

### Requirement: Consulta global de guardias (coordinación)
El sistema SHALL exponer un endpoint para COORDINADOR/ADMIN que liste todas las guardias del tenant con filtros.

#### Scenario: Coordinador consulta todas las guardias
- **WHEN** un coordinador accede al listado global de guardias
- **THEN** el sistema retorna todas las guardias del tenant
- **THEN** la respuesta incluye paginación

#### Scenario: Filtrar guardias por materia
- **WHEN** un coordinador filtra guardias por materia_id
- **THEN** el sistema retorna solo las guardias de esa materia

#### Scenario: Filtrar guardias por tutor
- **WHEN** un coordinador filtra guardias por asignacion_id
- **THEN** el sistema retorna solo las guardias de ese tutor

### Requirement: Exportar guardias
El sistema SHALL permitir exportar el listado de guardias en formato JSON estructurado.

#### Scenario: Exportar guardias sin filtros
- **WHEN** un coordinador solicita exportación de guardias
- **THEN** el sistema retorna todas las guardias del tenant como lista JSON
- **THEN** cada guardia incluye datos desnormalizados (materia nombre, tutor nombre)

#### Scenario: Exportar guardias filtradas
- **WHEN** un coordinador exporta guardias filtradas por materia_id
- **THEN** el sistema retorna solo las guardias que coinciden con el filtro
