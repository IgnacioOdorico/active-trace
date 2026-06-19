## ADDED Requirements

### Requirement: Vista transversal de encuentros (coordinación/admin)
La feature SHALL mostrar al usuario con permiso `encuentros:gestionar` todos los encuentros del tenant desde `GET /api/encuentros/instancias`, más allá del docente que los creó, para supervisión y monitoreo global, con su estado (realizado / pendiente), materia, fecha y enlaces.

#### Scenario: Listado global de encuentros
- **WHEN** el coordinador abre la vista admin de encuentros
- **THEN** la feature lista las instancias de todo el tenant con su estado y datos

#### Scenario: Filtrado de encuentros
- **WHEN** el coordinador filtra por materia
- **THEN** la feature solicita el listado acotado y muestra solo los encuentros de esa materia

### Requirement: Registro y consulta global de guardias
La feature SHALL permitir consultar el registro global de guardias desde `GET /api/guardias` con filtros, registrar guardias (`POST /api/guardias`), editarlas (`PATCH /api/guardias/{id}`) y exportar el registro (`GET /api/guardias/exportar`).

#### Scenario: Consulta filtrada de guardias
- **WHEN** el coordinador aplica filtros sobre el registro de guardias
- **THEN** la feature muestra las guardias coincidentes con quién cubrió, materia, día, horario, estado y comentarios

#### Scenario: Exportar registro de guardias
- **WHEN** el usuario pulsa "Exportar"
- **THEN** el navegador descarga el archivo generado por `GET /api/guardias/exportar`
