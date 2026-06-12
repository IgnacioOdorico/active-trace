## ADDED Requirements

### Requirement: Modelo ORM Aviso
El sistema SHALL tener un modelo ORM `Aviso` (tabla `aviso`) con los siguientes campos:
- `id`: UUID (PK, default uuid4)
- `tenant_id`: UUID (FK → Tenant)
- `alcance`: String(20) — Global | PorMateria | PorCohorte | PorRol
- `materia_id`: UUID (FK → Materia, nullable)
- `cohorte_id`: UUID (FK → Cohorte, nullable)
- `rol_destino`: String(20) nullable — rol destino (null = todos los roles)
- `severidad`: String(20) — Info | Advertencia | Crítico
- `titulo`: String(200)
- `cuerpo`: Text
- `inicio_en`: DateTime — desde cuándo es visible
- `fin_en`: DateTime — hasta cuándo es visible
- `orden`: Integer — prioridad de presentación (menor = más prioritario)
- `activo`: Boolean — permite preparar avisos antes de publicarlos
- `requiere_ack`: Boolean — si los destinatarios deben confirmar lectura
- `created_at`, `updated_at`, `deleted_at` (desde EntityMeta)

#### Scenario: Crear aviso exitosamente
- **WHEN** un COORDINADOR crea un aviso con alcance Global, severidad Info, título, cuerpo, vigencia y orden
- **THEN** el sistema persiste el aviso con id UUID y tenant_id del usuario
- **THEN** el estado activo es True por defecto
- **THEN** requiere_ack es False por defecto

#### Scenario: Crear aviso por materia
- **WHEN** un COORDINADOR crea un aviso con alcance PorMateria y un materia_id válido
- **THEN** el sistema persiste el aviso con el materia_id asociado

#### Scenario: Crear aviso sin datos obligatorios
- **WHEN** un usuario crea un aviso sin título ni alcance
- **THEN** el sistema rechaza la operación con error de validación

### Requirement: Modelo ORM AcknowledgmentAviso
El sistema SHALL tener un modelo ORM `AcknowledgmentAviso` (tabla `acknowledgment_aviso`) con los siguientes campos:
- `id`: UUID (PK, default uuid4)
- `aviso_id`: UUID (FK → Aviso)
- `usuario_id`: UUID (FK → Usuario)
- `confirmado_at`: DateTime — momento de la confirmación

#### Scenario: Confirmar lectura de aviso
- **WHEN** un usuario confirma la lectura de un aviso
- **THEN** el sistema crea un registro en AcknowledgmentAviso con aviso_id, usuario_id y la fecha/hora actual
