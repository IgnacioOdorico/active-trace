## ADDED Requirements

### Requirement: Modelo ORM Comunicacion
El sistema SHALL tener un modelo ORM `Comunicacion` (tabla `comunicacion`) con los siguientes campos:
- `id`: UUID (PK, default gen_random_uuid())
- `tenant_id`: UUID (FK → Tenant)
- `enviado_por`: UUID (FK → User)
- `materia_id`: UUID (FK → Materias)
- `destinatario`: String(500) — email cifrado con AES-256
- `asunto`: String(200)
- `cuerpo`: Text
- `lote_id`: UUID (nullable, agrupa envíos masivos)
- `intentos`: Integer (default 0, contador de reintentos del worker)
- `error_msg`: Text (nullable, último mensaje de error)
- `estado`: String(30) — Pendiente | Enviando | Enviado | Error | Cancelado | Nueva | PendienteAprobacion
- `enviado_at`: DateTime(timezone=True) (nullable)
- `enqueue_at`: DateTime(timezone=True) (nullable, cuándo se encoló)

#### Scenario: Crear comunicación exitosamente
- **WHEN** un usuario crea una comunicación con destinatario, asunto y cuerpo
- **THEN** el sistema persiste el registro con id UUID, tenant_id del usuario, estado "Nueva", intentos=0
- **THEN** el destinatario se almacena cifrado con prefijo `[cifrado]`

#### Scenario: Destinatario cifrado en reposo
- **WHEN** se consulta la tabla `comunicacion` directamente en SQL
- **THEN** la columna `destinatario` NO contiene el email en texto plano
- **THEN** la columna `destinatario` contiene el prefijo `[cifrado]` seguido de base64

### Requirement: Máquina de estados con transiciones válidas
El sistema SHALL validar que toda transición de estado en `Comunicacion` siga las reglas:

```
Nueva → Pendiente (si no requiere aprobación)
Nueva → PendienteAprobacion (si requiere aprobación)
PendienteAprobacion → Pendiente (aprobación)
PendienteAprobacion → Cancelado (rechazo)
Pendiente → Cancelado (cancelación manual)
Pendiente → Enviando (worker toma el mensaje)
Enviando → Enviado (éxito)
Enviando → Pendiente (error < 3 intentos)
Enviando → Error (error ≥ 3 intentos)
```

Cualquier otra transición SHALL ser rechazada con error de dominio.

#### Scenario: Transición válida Pendiente → Enviando
- **WHEN** el worker cambia estado de Pendiente a Enviando
- **THEN** la transición es aceptada

#### Scenario: Transición inválida Nueva → Enviado
- **WHEN** se intenta cambiar una comunicación en estado "Nueva" directamente a "Enviado"
- **THEN** el sistema rechaza la operación con un DomainError

#### Scenario: Transición inválida Cancelado → Pendiente
- **WHEN** se intenta cambiar una comunicación cancelada a Pendiente
- **THEN** el sistema rechaza la operación con un DomainError

### Requirement: Lote de comunicaciones (lote_id)
El sistema SHALL permitir agrupar comunicaciones bajo un mismo `lote_id` UUID para envíos masivos.

#### Scenario: Envío masivo genera mismo lote_id
- **WHEN** un usuario envía una comunicación a 10 destinatarios en una sola operación
- **THEN** las 10 comunicaciones SHALL compartir el mismo `lote_id`
- **THEN** el `lote_id` es un UUID diferente para cada operación de envío masivo

### Requirement: Campo requiere_aprobacion_comunicaciones en Tenant
El sistema SHALL añadir el campo booleano `requiere_aprobacion_comunicaciones` (default false) al modelo `Tenant`.

#### Scenario: Tenant sin aprobación
- **WHEN** `tenant.requiere_aprobacion_comunicaciones` es false
- **THEN** las comunicaciones nuevas se crean en estado "Nueva" y se transicionan directamente a "Pendiente"

#### Scenario: Tenant con aprobación
- **WHEN** `tenant.requiere_aprobacion_comunicaciones` es true
- **THEN** las comunicaciones nuevas se crean en estado "Nueva" y se transicionan a "PendienteAprobacion"
