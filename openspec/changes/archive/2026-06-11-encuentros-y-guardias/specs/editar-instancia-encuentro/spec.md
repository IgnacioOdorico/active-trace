## ADDED Requirements

### Requirement: Editar campos de una instancia de encuentro
El sistema SHALL permitir modificar los siguientes campos de una `InstanciaEncuentro` existente:
- `estado`: Programado ↔ Realizado ↔ Cancelado
- `meet_url`: enlace a la sala virtual
- `video_url`: enlace a la grabación (nullable)
- `comentario`: texto libre (nullable)

#### Scenario: Marcar encuentro como realizado
- **WHEN** un usuario cambia el estado de una instancia de "Programado" a "Realizado"
- **THEN** el sistema persiste el cambio
- **THEN** updated_at se actualiza

#### Scenario: Cancelar encuentro
- **WHEN** un usuario cambia el estado de una instancia de "Programado" a "Cancelado"
- **THEN** el sistema persiste el cambio

#### Scenario: Agregar video_url después de realizado
- **WHEN** un usuario agrega una video_url a una instancia en estado "Realizado"
- **THEN** el sistema persiste la URL de grabación

#### Scenario: Rechazar transición inválida
- **WHEN** un usuario intenta cambiar una instancia de estado "Cancelado" a "Realizado"
- **THEN** el sistema rechaza la operación con DomainError

#### Scenario: Encuentro no encontrado
- **WHEN** un usuario intenta editar una InstanciaEncuentro con un ID inexistente
- **THEN** el sistema retorna 404
