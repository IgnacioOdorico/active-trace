## ADDED Requirements

### Requirement: Crear encuentro único sin slot padre
El sistema SHALL permitir crear una `InstanciaEncuentro` sin asociarla a un `SlotEncuentro`. El campo `slot_id` debe ser NULL.

#### Scenario: Crear encuentro único exitosamente
- **WHEN** un usuario crea una InstanciaEncuentro con fecha, hora, titulo, meet_url y materia_id
- **THEN** el sistema persiste la instancia con estado "Programado"
- **THEN** el campo slot_id es NULL

#### Scenario: Encuentro único con datos mínimos
- **WHEN** un usuario crea una InstanciaEncuentro solo con fecha, hora, materia_id y titulo
- **THEN** el sistema persiste la instancia exitosamente
- **THEN** meet_url es NULL

#### Scenario: Rechazar encuentro único sin materia
- **WHEN** un usuario crea una InstanciaEncuentro sin materia_id
- **THEN** el sistema rechaza la operación
