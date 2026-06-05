## ADDED Requirements

### Requirement: BaseRepository se instancia con modelo y tenant_id
`BaseRepository[T]` SHALL recibir `model: type[T]` y `tenant_id: uuid.UUID` en el constructor. Toda instancia sin `tenant_id` SHALL ser inválida.

#### Scenario: Instanciación con tenant_id es válida
- **WHEN** se instancia `BaseRepository(Tenant, tenant_id=some_uuid)`
- **THEN** la instancia SHALL ser creada sin error

#### Scenario: Instanciación sin tenant_id falla en type-check
- **WHEN** se intenta instanciar `BaseRepository(Tenant)` sin `tenant_id`
- **THEN** el type checker SHALL marcar error (parámetro requerido)

### Requirement: BaseRepository.create persiste entidad con tenant_id
El método `create` SHALL recibir `session: AsyncSession` y `data: dict`, crear una instancia del modelo con `tenant_id` del repositorio, y hacer flush a la DB.

#### Scenario: Crear entidad con datos válidos
- **WHEN** se llama `repo.create(session, {"slug": "test", "name": "Test"})`
- **THEN** la entidad se persiste en la DB
- **AND** `entity.tenant_id` SHALL ser igual al `tenant_id` del repositorio

### Requirement: BaseRepository.get filtra por tenant_id y deleted_at
El método `get` SHALL recibir `session` e `id`, y retornar la entidad SOLO si cumple `tenant_id == self._tenant_id AND deleted_at IS NULL`.

#### Scenario: Get encuentra entidad del mismo tenant
- **WHEN** se busca un `id` que pertenece al tenant del repositorio y no está borrado
- **THEN** retorna la entidad

#### Scenario: Get no retorna entidad de otro tenant (aislamiento)
- **WHEN** se busca un `id` que NO pertenece al tenant del repositorio
- **THEN** retorna `None`

#### Scenario: Get no retorna entidad soft-deleted
- **WHEN** se busca un `id` que está soft-deleted (deleted_at IS NOT NULL)
- **THEN** retorna `None`

### Requirement: BaseRepository.get_all retorna solo entidades activas del tenant
El método `get_all` SHALL retornar solo entidades con `tenant_id == self._tenant_id AND deleted_at IS NULL`, a menos que `include_deleted=True`.

#### Scenario: get_all con filtro por tenant
- **WHEN** se llama `repo.get_all(session)`
- **THEN** solo retorna entidades del tenant del repositorio
- **AND** excluye entidades soft-deleted

#### Scenario: get_all incluyendo borrados
- **WHEN** se llama `repo.get_all(session, include_deleted=True)`
- **THEN** retorna entidades del tenant incluyendo soft-deleted

#### Scenario: Aislamiento multi-tenant en get_all
- **WHEN** existen entidades de dos tenants diferentes
- **AND** se llama `repo.get_all(session)` para tenant A
- **THEN** NO SHALL retornar entidades del tenant B

### Requirement: BaseRepository.update actualiza solo del mismo tenant
El método `update` SHALL recibir `session`, `id` y `data: dict`, lanzar `EntityNotFoundError` si la entidad no existe o no pertenece al tenant, y actualizar solo los campos presentes en `data`.

#### Scenario: Update entidad existente y del tenant
- **WHEN** se actualiza una entidad que existe y pertenece al tenant
- **THEN** los campos se modifican correctamente
- **AND** `updated_at` se actualiza

#### Scenario: Update entidad de otro tenant lanza error
- **WHEN** se actualiza una entidad que NO pertenece al tenant del repositorio
- **THEN** SHALL lanzar `EntityNotFoundError`

### Requirement: BaseRepository.soft_delete marca deleted_at
El método `soft_delete` SHALL setear `deleted_at` a la fecha/hora actual, sin eliminar el registro físicamente.

#### Scenario: Soft delete de entidad existente
- **WHEN** se llama `repo.soft_delete(session, id)`
- **THEN** `entity.deleted_at` SHALL ser un datetime no nulo
- **AND** el registro SHALL persistir en la DB

### Requirement: BaseRepository.count cuenta solo activos del tenant
El método `count` SHALL retornar la cantidad de registros del tenant con `deleted_at IS NULL`, opcionalmente filtrado por kwargs adicionales.

#### Scenario: Count básico
- **WHEN** se llama `repo.count(session)`
- **THEN** retorna el número de entidades activas del tenant
