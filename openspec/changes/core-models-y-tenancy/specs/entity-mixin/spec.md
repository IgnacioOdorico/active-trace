## ADDED Requirements

### Requirement: EntityMeta provee id UUID como PK
Toda entidad de dominio SHALL tener un `id` de tipo UUID como primary key, generado automáticamente con `uuid.uuid4()`.

#### Scenario: Entidad creada tiene UUID auto-generado
- **WHEN** se crea una instancia de una entidad que hereda EntityMeta
- **THEN** `id` SHALL ser un UUID no nulo asignado automáticamente
- **AND** cada entidad SHALL tener un `id` único

### Requirement: EntityMeta provee tenant_id como FK obligatoria
EntityMeta SHALL declarar `tenant_id` como columna UUID con FK a `tenant.id` y NOT NULL.

#### Scenario: Entidad con tenant_id se persiste correctamente
- **WHEN** se crea una entidad con un `tenant_id` válido que existe en la tabla `tenant`
- **THEN** la entidad se persiste con ese `tenant_id`

#### Scenario: Entidad con tenant_id inexistente es rechazada
- **WHEN** se crea una entidad con un `tenant_id` que no existe en la tabla `tenant`
- **THEN** la DB SHALL rechazar con violación de FK

### Requirement: EntityMeta provee timestamps created_at y updated_at
EntityMeta SHALL declarar `created_at` (server_default=func.now()) y `updated_at` (server_default + onupdate=func.now()), ambos con timezone.

#### Scenario: created_at se asigna al crear
- **WHEN** se crea una entidad
- **THEN** `created_at` SHALL ser un datetime con timezone no nulo

#### Scenario: updated_at se actualiza al modificar
- **WHEN** se modifica una entidad existente
- **THEN** `updated_at` SHALL ser posterior a `created_at`

### Requirement: EntityMeta provee soft delete via deleted_at
EntityMeta SHALL declarar `deleted_at` como DateTime(timezone=True) nullable, default None.

#### Scenario: Entidad nueva tiene deleted_at NULL
- **WHEN** se crea una entidad
- **THEN** `deleted_at` SHALL ser NULL

#### Scenario: Soft delete asigna deleted_at
- **WHEN** se ejecuta soft delete sobre una entidad
- **THEN** `deleted_at` SHALL ser un datetime no nulo
- **AND** el registro NO SHALL ser eliminado físicamente de la DB
