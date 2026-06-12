## ADDED Requirements

### Requirement: AuditLogService.acciones_por_dia()

The system SHALL add an `acciones_por_dia()` method to `AuditLogService` that returns action volume aggregated by day.

Signature:
```python
async def acciones_por_dia(
    self,
    db: AsyncSession,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    materia_id: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    accion: str | None = None,
    materias_ids: list[uuid.UUID] | None = None,
) -> list[dict]
```

The `materias_ids` parameter SHALL be used for `(propio)` scope filtering — when provided, only entries for those materias are included. When `None`, no materia filter is applied.

The method SHALL delegate to `AuditLogRepository.acciones_por_dia()`.

#### Scenario: Service returns daily action counts
- **WHEN** `AuditLogService.acciones_por_dia()` is called with default params
- **THEN** returns a list of `{fecha: date, total: int}` for the last 30 days

#### Scenario: Service applies materia filter
- **WHEN** called with `materias_ids=["uuid1", "uuid2"]`
- **THEN** results are filtered to those materias only

### Requirement: AuditLogService.comunicaciones_por_docente()

The system SHALL add a `comunicaciones_por_docente()` method to `AuditLogService`.

Signature:
```python
async def comunicaciones_por_docente(
    self,
    db: AsyncSession,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    materia_id: uuid.UUID | None = None,
    materias_ids: list[uuid.UUID] | None = None,
) -> list[dict]
```

The method SHALL only consider actions with codes starting with `COMUNICACION_`.

#### Scenario: Service returns communication status by docente
- **WHEN** `AuditLogService.comunicaciones_por_docente()` is called
- **THEN** returns communication status aggregated by docente

### Requirement: AuditLogService.interacciones_por_docente_materia()

The system SHALL add an `interacciones_por_docente_materia()` method to `AuditLogService`.

Signature:
```python
async def interacciones_por_docente_materia(
    self,
    db: AsyncSession,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    materia_id: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    materias_ids: list[uuid.UUID] | None = None,
) -> list[dict]
```

#### Scenario: Service returns interaction metrics
- **WHEN** called with valid parameters
- **THEN** returns metrics grouped by docente and materia with action type breakdown

### Requirement: AuditLogService.ultimas_acciones()

The system SHALL add an `ultimas_acciones()` method to `AuditLogService`.

Signature:
```python
async def ultimas_acciones(
    self,
    db: AsyncSession,
    max_resultados: int = 200,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    materia_id: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    accion: str | None = None,
    materias_ids: list[uuid.UUID] | None = None,
) -> list[AuditLog]
```

The `max_resultados` SHALL be capped at 1000.

#### Scenario: Service returns recent actions
- **WHEN** called with default params
- **THEN** returns the 200 most recent AuditLog entries

#### Scenario: Max enforced at service level
- **WHEN** called with `max_resultados=5000`
- **THEN** returns at most 1000 entries
