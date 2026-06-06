## ADDED Requirements

### Requirement: DomainError es base de excepciones de dominio
`DomainError` SHALL ser una clase abstracta que hereda de `Exception` con campos `detail: str` y `context: dict`. Todas las excepciones de dominio SHALL heredar de `DomainError`.

#### Scenario: DomainError lleva detail y context
- **WHEN** se instancia `DomainError(detail="Error", context={"key": "value"})`
- **THEN** `detail` SHALL ser accesible como atributo
- **AND** `context` SHALL ser un diccionario

### Requirement: TenantNotFoundError para tenant inexistente
`TenantNotFoundError` SHALL recibir `tenant_id: uuid.UUID`, setear `detail="Tenant not found"` y `context={"tenant_id": str(tenant_id)}`.

#### Scenario: Creación de TenantNotFoundError
- **WHEN** se instancia `TenantNotFoundError(tenant_id=some_uuid)`
- **THEN** `detail` SHALL ser `"Tenant not found"`
- **AND** `context["tenant_id"]` SHALL ser el UUID como string

### Requirement: EntityNotFoundError para entidad no encontrada
`EntityNotFoundError` SHALL recibir `entity_type: str` (nombre de la clase) y `entity_id: uuid.UUID`. El detail SHALL ser `"{entity_type} with id {entity_id} not found"`.

#### Scenario: Creación de EntityNotFoundError
- **WHEN** se instancia `EntityNotFoundError(entity_type="Tenant", entity_id=some_uuid)`
- **THEN** `detail` SHALL contener el nombre y el UUID
- **AND** `context` SHALL incluir `entity_type` y `entity_id`

### Requirement: EncryptionError para fallos de crypto
`EncryptionError` SHALL recibir un mensaje opcional. SHALL usarse cuando falla el descifrado (ciphertext inválido, key incorrecta, padding corrupto).

#### Scenario: EncryptionError con mensaje
- **WHEN** se instancia `EncryptionError("Invalid padding")`
- **THEN** `detail` SHALL ser el mensaje provisto
- **AND** NO SHALL exponer el ciphertext ni la key en el mensaje
