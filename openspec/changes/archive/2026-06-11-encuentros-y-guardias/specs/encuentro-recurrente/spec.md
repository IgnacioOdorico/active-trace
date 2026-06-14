## ADDED Requirements

### Requirement: Generación de instancias recurrentes (RN-13)
El sistema SHALL generar automáticamente N instancias de `InstanciaEncuentro` al crear un `SlotEncuentro` con `cant_semanas > 0`. Cada instancia representa un encuentro en una fecha semanal sucesiva desde `fecha_inicio`.

#### Scenario: Generar 8 instancias semanales
- **WHEN** un usuario crea un SlotEncuentro con dia_semana="Miércoles", fecha_inicio="2026-04-01", cant_semanas=8
- **THEN** el sistema genera 8 InstanciaEncuentro
- **THEN** la primera instancia tiene fecha "2026-04-01"
- **THEN** la segunda instancia tiene fecha "2026-04-08"
- **THEN** la octava instancia tiene fecha "2026-05-20"

#### Scenario: Validar coincidencia fecha_inicio con dia_semana
- **WHEN** un usuario crea un SlotEncuentro con dia_semana="Lunes" y fecha_inicio="2026-04-01" (que NO es lunes)
- **THEN** el sistema rechaza la operación con DomainError
- **THEN** ninguna instancia es creada

#### Scenario: cant_semanas máximo permitido
- **WHEN** un usuario crea un SlotEncuentro con cant_semanas > 52
- **THEN** el sistema rechaza la operación con error de validación

#### Scenario: Transacción atómica en generación
- **WHEN** ocurre un error durante la generación de la 5ta instancia (de 10)
- **THEN** el sistema revierte toda la transacción
- **THEN** ninguna instancia es persistida
- **THEN** el slot NO es creado

### Requirement: Editar una instancia no afecta al slot ni a otras instancias
El sistema SHALL permitir editar cada instancia individualmente sin propagar cambios al slot padre ni a otras instancias del mismo slot.

#### Scenario: Editar instancia individual
- **WHEN** un usuario cambia el meet_url de una instancia específica
- **THEN** las demás instancias del mismo slot conservan su meet_url original
- **THEN** el slot padre conserva su meet_url original
