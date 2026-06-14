## ADDED Requirements

### Requirement: AuditLogService

The system SHALL provide `AuditLogService(tenant_id: uuid.UUID)` with:
- A `BaseRepository[AuditLog]` internally (read-only operations only)
- A custom `log()` method for creating audit entries
- Action code constants as class-level or module-level variables
- No `update()`, `delete()`, or `soft_delete()` — the repository SHALL only expose `create()` and read methods

The `log()` method SHALL accept:
- `db: AsyncSession`
- `actor_id: uuid.UUID`
- `accion: str` (from standardized codes)
- `impersonado_id: uuid.UUID | None = None`
- `materia_id: uuid.UUID | None = None`
- `detalle: dict | None = None`
- `filas_afectadas: int = 0`
- `ip: str | None = None`
- `user_agent: str | None = None`

The `log()` method SHALL NOT require an explicit commit — the caller commits the transaction.

#### Scenario: Service creates audit entry
- **WHEN** `AuditLogService.log()` is called with valid parameters
- **THEN** a new AuditLog record is inserted into the database
- **AND** the record has all provided fields set correctly

#### Scenario: Service raises on update attempt
- **WHEN** code calls `update()` or `soft_delete()` via the repository
- **THEN** the system raises an error (operation not supported)

### Requirement: audit_log decorator/utility

The system SHALL provide a reusable `log_action` helper function that can be called from any service:

```python
async def log_action(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    actor_id: uuid.UUID,
    accion: str,
    impersonado_id: uuid.UUID | None = None,
    materia_id: uuid.UUID | None = None,
    detalle: dict | None = None,
    filas_afectadas: int = 0,
    ip: str | None = None,
    user_agent: str | None = None,
) -> None
```

This function SHALL instantiate `AuditLogService` internally and call its `log()` method.

The system MAY also provide a decorator form `@audit_log(accion="...")` that automatically captures `actor_id` from the current user dependency and `ip`/`user_agent` from the request.

#### Scenario: Helper creates audit entry
- **WHEN** `log_action()` is called from any service
- **THEN** an audit entry is created with the provided parameters

#### Scenario: Decorator captures context automatically
- **WHEN** a function decorated with `@audit_log(accion="PADRON_CARGAR")` is called
- **THEN** the decorator reads `actor_id` from the user context and creates an audit entry after the function executes

### Requirement: IP and user_agent capture

The system SHALL capture `ip` and `user_agent` from the incoming HTTP request when using the decorator or when explicitly passed to `log_action()`.

#### Scenario: IP captured from request
- **WHEN** a request triggers audit logging via the decorator
- **THEN** the client IP address is extracted from the request headers
