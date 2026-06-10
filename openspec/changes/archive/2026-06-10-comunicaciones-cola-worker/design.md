## Context

C-10 y C-11 establecieron calificaciones, umbrales y análisis de alumnos atrasados. El flujo central del PROFESOR (FL-02) culmina con la comunicación a los alumnos detectados (pasos 7-8). Actualmente no existe modelo `Comunicacion`, worker de cola ni endpoints de envío.

El proyecto ya cuenta con:
- `app/core/security.py` con `encrypt()`/`decrypt()` AES-256-CBC para datos `[cifrado]` (reutilizado de `Usuario.email`).
- `backend/app/workers/main.py` como placeholder no-op (loop de 1 hora).
- Patrón Clean Architecture establecido: Models → Repositories → Services → Routers.
- `BaseRepository` con filtro `tenant_id` automático.
- `AuditLogService` con constantes de acción (`CALIFICACIONES_IMPORTAR`, etc.).

ADR-003 (worker de cola) está pendiente. Este change implementa el worker como asyncio propio (sin Celery/ARQ) para minimizar dependencias, siguiendo el principio de mínima sorpresa y simplicidad operativa.

## Goals / Non-Goals

**Goals:**
- Modelo `Comunicacion` con destinatario `[cifrado]`, `lote_id`, máquina de estados machine-driven.
- Worker asíncrono que procesa `Pendiente → Enviando → Enviado/Error` con backoff (< 3 → Pendiente, ≥ 3 → Error).
- Preview obligatorio con sustitución de variables (F3.1, RN-16).
- Aprobación humana configurable por tenant (F3.3, RN-17): `Nueva → PendienteAprobacion → [aprobar] → Pendiente`.
- Endpoints REST `/api/comunicaciones/*` con guards `comunicacion:enviar` y `comunicacion:aprobar`.
- Audit log con código `COMUNICACION_ENVIAR`.
- Tests de máquina de estados, preview, aprobación, worker, cifrado.

**Non-Goals:**
- No se implementa integración con proveedor SMTP real (mock/stub para desarrollo).
- No se implementa frontend de comunicaciones.
- No se implementa mensajería interna (F3.4) ni tablón de avisos (F3.5).
- No se implementa dashboard de estado de comunicaciones (F9.1 sub-vista comunicaciones).

## Decisions

### D1: Modelo Comunicacion con columna estado enum en texto
- **Decisión**: `estado` se almacena como `String(30)` en DB (no enum nativo de PostgreSQL), con un enum Python `EstadoComunicacion` en el modelo para type safety.
- **Alternativa considerada**: Enum nativo PostgreSQL.
- **Razón**: Consistencia con el resto del modelo (`User.estado`, `Calificacion.origen`). Los enum nativos de PG son más rígidos para migraciones. El enum Python con validación en Service es suficiente.

### D2: Worker asyncio simple (sin Celery/ARQ)
- **Decisión**: El worker es un loop asyncio que pool ea la DB cada N segundos buscando `Comunicacion` con `estado=Pendiente`, las procesa secuencialmente y actualiza estados. El entrypoint vive en `workers/main.py` que también puede disparar otros workers futuros.
- **Alternativa considerada**: Celery con Redis, ARQ (Redis-backed).
- **Razón**: Este change resuelve ADR-003 con la opción más simple. Redis añade complejidad operativa innecesaria para una cola que se procesa en el mismo servidor PostgreSQL. El polling sobre la tabla `comunicacion` es transaccional, evita reintentos fantasmas y da visibilidad inmediata del estado. Si el volumen futuro lo requiere, se migra a Redis sin cambiar el modelo de datos.

### D3: Destinatario cifrado con encrypt()/decrypt() existente
- **Decisión**: El campo `destinatario` de `Comunicacion` se cifra con `app.core.security.encrypt()` al persistir y se descifra con `decrypt()` al leer para preview o envío.
- **Alternativa considerada**: Cifrado a nivel de aplicación en Service vs. en Repository.
- **Razón**: Sigue el patrón exacto de `UsuarioRepository.get_by_email()` — el cifrado/descifrado ocurre en la capa Service (al crear la comunicación y al preparar el envío). El Repository persiste el valor cifrado tal cual.

### D4: Máquina de estados con validación en Service
- **Decisión**: `ComunicacionService` expone métodos `enqueue()`, `approve()`, `cancel()`, `process()` que validan la transición de estado antes de mutar. Estados y transiciones válidas se definen como constantes/dict en el Service.
- **Alternativa considerada**: State machine library externa (transitions, statemachine).
- **Razón**: La máquina tiene 5 estados y ~7 transiciones válidas. Una biblioteca externa añade complejidad innecesaria. Un dict de transiciones válidas en Python es más legible y testeable.

```
Transiciones válidas:
  Nueva → Pendiente (si no requiere aprobación)
  Nueva → PendienteAprobacion (si requiere aprobación)
  PendienteAprobacion → Pendiente (aprobación)
  PendienteAprobacion → Cancelado (rechazo)
  Pendiente → Cancelado (cancelación manual)
  Pendiente → Enviando (worker toma el mensaje)
  Enviando → Enviado (éxito)
  Enviando → Pendiente (error < 3 intentos, backoff)
  Enviando → Error (error ≥ 3 intentos)
```

### D5: lote_id como UUID generado al encolar
- **Decisión**: Al crear un envío masivo, el Service genera un UUID `lote_id` compartido por todas las comunicaciones del lote. El worker puede procesar todo el lote o fallar comunicaciones individuales.
- **Alternativa considerada**: Lote como tabla separada.
- **Razón**: Una columna `lote_id` en la misma tabla simplifica el modelo. No hay comportamiento de lote que justifique una entidad separada. La agrupación se hace por query (`WHERE lote_id = X`).

### D6: Aprobación configurable en Tenant
- **Decisión**: Se añade `requiere_aprobacion_comunicaciones: bool` (default `false`) al modelo `Tenant`. Si es `true`, toda comunicación nueva creada viaja a `PendienteAprobacion` en lugar de `Pendiente`. El guard `comunicacion:aprobar` controla quién puede aprobar/rechazar.
- **Alternativa considerada**: Configuración por router/endpoint.
- **Razón**: La regla de negocio (RN-17) es por tenant, no por usuario. Modelarlo en `Tenant` es semánticamente correcto y evita lógica condicional dispersa en los endpoints.

### D7: Plantillas con string.Template
- **Decisión**: Las plantillas de asunto/cuerpo usan `string.Template` de la stdlib con variables `$nombre`, `$materia`, `$comision`.
- **Alternativa considerada**: Jinja2.
- **Razón**: Las plantillas son simples (3-4 variables de sustitución). `string.Template` evita una dependencia externa y es seguro por defecto (no ejecuta código).

## Risks / Trade-offs

- **[Riesgo] Worker polling satura DB**: si el intervalo de polling es muy corto, el worker puede generar carga innecesaria en PostgreSQL. → **Mitigación**: intervalo configurable vía variable de entorno `WORKER_POLL_INTERVAL` (default 10s). Para picos, se puede reducir sin deploy.
- **[Riesgo] Concurrencia: dos workers procesan la misma comunicación**: si se escalan múltiples réplicas del worker, pueden tomar el mismo `Pendiente` simultáneamente. → **Mitigación**: `UPDATE ... WHERE estado = 'Pendiente' RETURNING *` con transacción atómica. Solo un worker gana; el resto no encuentra filas en estado Pendiente.
- **[Riesgo] Error de envío permanente (bounce)**: un destinatario inválido generará reintentos infinitos. → **Mitigación**: límite de 3 reintentos con backoff. Al 3er error → estado `Error`. Se requiere intervención manual para reencolar.
- **[Trade-off] Polling vs. push**: polling PostgreSQL cada N segundos no es tan eficiente como una cola push (Redis pub/sub). → **Razon**: Para el volumen esperado (decenas a cientos de comunicaciones por hora), polling es perfectamente adecuado. Redis añade un punto de fallo y complejidad operativa sin beneficio real a esta escala.
- **[Riesgo] Destinatario cifrado no se puede consultar en SQL**: buscar comunicaciones por email destino requiere descifrar en Python. → **Mitigación**: Las búsquedas por destinatario se hacen a nivel Service (descifra y filtra in-memory), igual que `UsuarioRepository.get_by_email()`.

## Migration Plan

1. Crear migración Alembic `009`:
   - `CREATE TABLE comunicacion (...)` con columnas del modelo.
   - `ALTER TABLE tenant ADD COLUMN requiere_aprobacion_comunicaciones BOOLEAN NOT NULL DEFAULT false`.
2. Deploy modelo, repositorio, servicio y routers (API endpoints nuevos, sin cambios rompedores).
3. Deploy worker actualizado (el placeholder es compatible hacia atrás).
4. Rollback: `DROP TABLE comunicacion`, `ALTER TABLE tenant DROP COLUMN`, revert worker a placeholder.
