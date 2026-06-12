## ADDED Requirements

### Requirement: Modelo ORM SlotEncuentro
El sistema SHALL tener un modelo ORM `SlotEncuentro` (tabla `slot_encuentro`) con los siguientes campos:
- `id`: UUID (PK, default uuid4)
- `tenant_id`: UUID (FK → Tenant)
- `asignacion_id`: UUID (FK → Asignacion, quien crea el slot)
- `materia_id`: UUID (FK → Materia)
- `titulo`: String(200)
- `hora`: Time — horario del encuentro
- `dia_semana`: String(15) — Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo
- `fecha_inicio`: Date — inicio de la recurrencia
- `cant_semanas`: Integer — cuántas instancias genera (0 si es fecha única)
- `fecha_unica`: Date (nullable) — alternativa a recurrencia: un encuentro puntual
- `meet_url`: String(500) — enlace a la sala virtual
- `vig_desde`: Date
- `vig_hasta`: Date (nullable)
- `created_at`, `updated_at`, `deleted_at` (desde EntityMeta)

#### Scenario: Crear slot recurrente exitosamente
- **WHEN** un usuario crea un SlotEncuentro con cant_semanas=8, dia_semana="Lunes", fecha_inicio="2026-03-02"
- **THEN** el sistema persiste el slot con id UUID y tenant_id del usuario
- **THEN** el sistema genera 8 InstanciaEncuentro (una por semana desde fecha_inicio)

#### Scenario: Crear slot de fecha única
- **WHEN** un usuario crea un SlotEncuentro con cant_semanas=0 y fecha_unica="2026-03-15"
- **THEN** el sistema persiste el slot
- **THEN** el sistema genera 1 InstanciaEncuentro en fecha_unica

#### Scenario: Slot con datos faltantes rechazado
- **WHEN** un usuario crea un SlotEncuentro sin titulo ni materia_id
- **THEN** el sistema rechaza la operación con error de validación

### Requirement: Modelo ORM InstanciaEncuentro
El sistema SHALL tener un modelo ORM `InstanciaEncuentro` (tabla `instancia_encuentro`) con los siguientes campos:
- `id`: UUID (PK, default uuid4)
- `tenant_id`: UUID (FK → Tenant)
- `slot_id`: UUID (FK → SlotEncuentro, nullable si es independiente)
- `materia_id`: UUID (FK → Materia)
- `fecha`: Date
- `hora`: Time
- `titulo`: String(200)
- `estado`: String(20) — Programado|Realizado|Cancelado
- `meet_url`: String(500)
- `video_url`: String(500) (nullable)
- `comentario`: Text (nullable)
- `created_at`, `updated_at`, `deleted_at` (desde EntityMeta)

#### Scenario: Crear instancia como parte de slot recurrente
- **WHEN** el servicio genera instancias desde un SlotEncuentro
- **THEN** cada InstanciaEncuentro tiene slot_id al slot padre
- **THEN** cada instancia hereda titulo, hora, meet_url del slot
- **THEN** la fecha se calcula como fecha_inicio + (semana_i * 7 días)

#### Scenario: Instancia sin slot padre
- **WHEN** se crea una InstanciaEncuentro sin slot_id
- **THEN** el campo slot_id es NULL
- **THEN** la instancia es independiente y editable sin restricciones

#### Scenario: Estado inicial de instancia
- **WHEN** el sistema crea una nueva InstanciaEncuentro
- **THEN** el estado inicial es "Programado"
