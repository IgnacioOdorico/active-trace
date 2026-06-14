## ADDED Requirements

### Requirement: El sistema SHALL modelar el padrón como versionado
`VersionPadron` representa una carga de padrón para una materia×cohorte. Solo una versión puede estar activa por par (materia_id, cohorte_id).
`EntradaPadron` contiene los alumnos de esa versión: nombre, apellidos, email [cifrado], comisión, regional, usuario_id (nullable).

#### Scenario: Crear versión de padrón
- **WHEN** se crea una VersionPadron para materia X, cohorte Y
- **THEN** el sistema crea la versión en estado inactivo

#### Scenario: Activar versión desactiva la anterior
- **WHEN** se activa una nueva versión para materia X, cohorte Y
- **THEN** la versión anterior activa pasa a inactiva automáticamente

### Requirement: El sistema SHALL permitir importar padrón desde archivo .xlsx/.csv
El endpoint `POST /api/padron/importar` DEBE aceptar un archivo, procesarlo y mostrar vista previa antes de confirmar.
Los formatos aceptados son .xlsx y .csv con columnas: nombre, apellidos, email, comisión, regional.

#### Scenario: Importar padrón con vista previa
- **WHEN** se sube un archivo .xlsx válido a POST /api/padron/importar?preview=true
- **THEN** el sistema retorna 200 con la vista previa (N filas detectadas) sin persistir

#### Scenario: Confirmar importación
- **WHEN** se envía POST /api/padron/importar?confirmar=true con el mismo archivo
- **THEN** el sistema crea la VersionPadron y las EntradaPadron
- **AND** los emails se almacenan cifrados

#### Scenario: Importar sin permiso retorna 403
- **WHEN** se envía POST /api/padron/importar sin permiso `padron:importar`
- **THEN** el sistema retorna 403

#### Scenario: Importar archivo con formato inválido retorna 422
- **WHEN** se sube un archivo que no es .xlsx ni .csv
- **THEN** el sistema retorna 422

### Requirement: El sistema SHALL permitir vaciar datos de materia (RN-04)
El endpoint `DELETE /api/padron/materia/{id}/vaciar` DEBE eliminar (soft delete) todas las versiones de padrón y entradas asociadas a una materia, pero solo para el tenant del usuario.

#### Scenario: Vaciar materia exitoso
- **WHEN** se envía DELETE /api/padron/materia/{id}/vaciar
- **THEN** el sistema marca deleted_at en todas las versiones y entradas de esa materia

### Requirement: La importación SHALL generar audit PADRON_CARGAR
Cada importación confirmada DEBE registrar un audit log con código `PADRON_CARGAR` y filas_afectadas.

#### Scenario: Importación genera audit
- **WHEN** se confirma una importación de 50 alumnos
- **THEN** el sistema registra audit con accion="PADRON_CARGAR" y filas_afectadas=50
