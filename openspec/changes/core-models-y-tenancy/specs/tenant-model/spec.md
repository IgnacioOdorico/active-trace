## ADDED Requirements

### Requirement: Tenant tiene slug único como identificador de negocio
El sistema SHALL almacenar cada tenant con un slug único alfanumérico que lo identifica en URLs y APIs externas. El slug SHALL ser inmutable después de creado.

#### Scenario: Crear tenant con slug único
- **WHEN** se crea un tenant con slug "universidad-nacional"
- **THEN** el tenant se persiste con ese slug
- **AND** la columna `slug` en la tabla `tenant` tiene una constraint UNIQUE

#### Scenario: Crear tenant con slug duplicado
- **WHEN** se crea un segundo tenant con slug "universidad-nacional"
- **THEN** la operación SHALL fallar con violación de unique constraint

### Requirement: Tenant tiene nombre legible y configuración JSON
El sistema SHALL almacenar el nombre comercial del tenant (VARCHAR(255)) y un campo `config` de tipo JSONB con configuración arbitraria del inquilino (tema, preferencias regionales, etc.).

#### Scenario: Crear tenant con configuración completa
- **WHEN** se crea un tenant con `name="Universidad Nacional"` y `config={"theme": "blue", "locale": "es-AR"}`
- **THEN** ambos valores se persisten correctamente
- **AND** `config` SHALL ser un campo JSONB

#### Scenario: Config por defecto es objeto vacío
- **WHEN** se crea un tenant sin proporcionar `config`
- **THEN** `config` SHALL default a `{}`

### Requirement: Tenant hereda EntityMeta
El modelo Tenant SHALL heredar de `EntityMeta` para obtener `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`.

#### Scenario: Tenant creado tiene timestamps automáticos
- **WHEN** se crea un tenant
- **THEN** `created_at` y `updated_at` SHALL ser asignados automáticamente por la DB
- **AND** `deleted_at` SHALL ser NULL

### Requirement: Tenant se referencia desde todas las entidades de dominio
Toda entidad de dominio SHALL referenciar al tenant mediante una FK a `tenant.id` en la columna `tenant_id`.

#### Scenario: FK tenant_id es obligatoria
- **WHEN** se intenta crear una entidad sin `tenant_id`
- **THEN** la DB SHALL rechazar la operación por violación de NOT NULL
