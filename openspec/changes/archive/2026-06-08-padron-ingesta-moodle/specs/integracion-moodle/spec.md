## ADDED Requirements

### Requirement: El sistema SHALL integrarse con Moodle Web Services
El módulo `integrations/moodle_ws.py` DEBE implementar un cliente para la API estándar de Moodle WS.
Debe poder sincronizar usuarios (alumnos) y actividades de una materia.

#### Scenario: Sync on-demand exitosa
- **WHEN** se invoca sync on-demand para materia X, cohorte Y
- **AND** Moodle responde correctamente
- **THEN** el sistema importa los alumnos como nueva versión de padrón

#### Scenario: Moodle WS no disponible retorna 502
- **WHEN** Moodle no responde después de 3 reintentos con backoff exponencial
- **THEN** el sistema retorna 502 Bad Gateway con mensaje claro

#### Scenario: Fallback a import manual
- **WHEN** Moodle WS falla
- **THEN** el sistema permite al usuario subir un archivo .xlsx/.csv como alternativa

### Requirement: El sistema SHALL tener sync nocturna automática
El worker DEBE ejecutar una sincronización nocturna programada para todas las materias con integración Moodle habilitada.

#### Scenario: Sync nocturna procesa materias activas
- **WHEN** se ejecuta la sync nocturna
- **THEN** el sistema sincroniza todas las materias con integración Moodle activa
- **AND** registra el resultado en audit log
