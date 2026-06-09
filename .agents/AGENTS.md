# AGENTS.md — active-trace
> Contrato operativo para OpenCode en este repositorio.
> **Al iniciar cualquier sesión: ejecutar el bloque SETUP AUTOMÁTICO antes de cualquier otra acción.**

---

## SETUP AUTOMÁTICO

> Ejecutar estos pasos en orden al arrancar. No empezar ningún change sin completarlos.

### Paso 1 — Cargar skills

Leer el contenido de cada URL y mantenerlo en contexto de trabajo durante toda la sesión:

```
https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md
https://raw.githubusercontent.com/anthropics/skills/main/skills/xlsx/SKILL.md
https://raw.githubusercontent.com/anthropics/skills/main/skills/pdf/SKILL.md
https://raw.githubusercontent.com/anthropics/skills/main/skills/pdf-reading/SKILL.md  (si existe, sino ignorar)
https://raw.githubusercontent.com/anthropics/skills/main/skills/docx/SKILL.md
https://raw.githubusercontent.com/anthropics/skills/main/skills/pptx/SKILL.md
https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md
```

Tabla de cuándo aplicar cada skill:

| Skill | Usar en estos changes / situaciones |
|---|---|
| `frontend-design` | C-21, C-22, C-23, C-24 — cualquier componente React o Tailwind |
| `xlsx` | C-08 (export equipos), C-09 (import padrón), C-10 (import calificaciones), C-18 (liquidaciones) |
| `pdf` | C-11 (reportes), C-17 (programas de materia), C-18 (liquidaciones descargables) |
| `pdf-reading` | Leer `activia-trace-documentacion.pdf` o cualquier PDF subido por el usuario |
| `docx` | Reportes Word, programas de materia en .docx, comunicaciones formales |
| `pptx` | Presentaciones de avance, decks de capacitación |
| `skill-creator` | Cuando se necesite crear o mejorar una skill del proyecto |

### Paso 2 — Leer estado del proyecto

```
LEER: CHANGES.md
  → identificar qué changes tienen [x] y cuáles [ ]
  → determinar el próximo change disponible según el árbol de dependencias

LEER: knowledge-base/<archivos indicados en "Leer antes" del change activo>
```

### Paso 3 — Confirmar antes de empezar

Responder con este bloque exacto antes de cualquier otra acción:

```
✅ SETUP COMPLETO — active-trace
Skills cargadas: [listar las que respondieron OK]
Completados: C-01, C-02, C-03, C-04, C-05, C-06, C-07
Pendientes: C-08 → C-24
Próximo disponible: C-09 (padron-ingesta-moodle) [MEDIO]
Esperando instrucción.
```

---

## 1. Identidad del proyecto

**active-trace** es una plataforma educativa multi-tenant para instituciones universitarias.
Gestiona alumnos, calificaciones, comunicaciones, equipos docentes, liquidaciones y auditoría completa — todo aislado por tenant (institución).

**Usuarios:** Alumnos, Tutores, Profesores, Coordinadores, Nexos, Administradores, Finanzas.

**Principio rector:** Ningún dato de un tenant puede ser visible para otro. Este aislamiento es arquitectónico, no opcional.

---

## 2. Stack y arquitectura

### Backend
- **Python 3.12** — FastAPI (async), Pydantic v2, SQLAlchemy 2.0 async, Alembic
- **DB:** PostgreSQL 16, driver asyncpg
- **Auth:** JWT (python-jose), rotación de refresh, 2FA TOTP, Argon2id para passwords
- **Cifrado en reposo:** AES-256 para campos PII (email, DNI, CUIL, CBU)
- **Worker:** proceso Python separado para la cola de comunicaciones
- **Observabilidad:** OpenTelemetry + logging estructurado JSON
- **Tests:** pytest + httpx async, cobertura mínima 80%

### Frontend (se crea en C-21)
- **React 18 + TypeScript + Vite**
- **Styling:** Tailwind CSS (clases base, sin compiler custom)
- **Estado servidor:** TanStack Query
- **Formularios:** React Hook Form + Zod
- **HTTP:** Axios con interceptor de auth + refresh transparente

### Infraestructura
- Docker Compose: servicios `api`, `postgres`, `worker`
- Deploy: convención Easypanel
- Configuración: todo en `.env`, nunca hardcodeado en código

---

## 3. Reglas de código irrompibles

No tienen excepciones. Violarlas es motivo de rechazo.

### Generales
- **≤ 500 LOC por archivo.** Si crece más, refactorizar antes de agregar.
- **Sin lógica de negocio en routers.** Routers validan → delegan a Services → devuelven respuesta.
- **Sin SQL en Services.** Services → Repositories → DB. Sin saltear capas.
- **Todo endpoint tiene guard declarado** (`require_permission("modulo:accion")`). Sin guard = PR rechazado.
- **Soft delete siempre.** Nunca `DELETE` físico. Usar `deleted_at`.
- **PII nunca en logs.** `email`, `dni`, `cuil`, `cbu`, `alias_cbu` no aparecen en logs ni respuestas de error.
- **Identidad solo del JWT verificado.** Nunca confiar en `user_id`/`tenant_id` que vengan en body o query params.

### Python
- `async def` en todos los endpoints y métodos de repositorio.
- Imports absolutos únicamente.
- Type hints en todas las funciones. Pydantic v2 para todos los schemas.
- Nunca `print()` — usar el logger estructurado.
- Excepciones propias en `app/core/exceptions.py`. Nunca `raise Exception("...")` crudo.

### React / TypeScript
- Tokens en memoria del interceptor, nunca en `localStorage` / `sessionStorage`.
- Formularios con React Hook Form + Zod. Nunca `useState` para campos de formulario.
- Rutas protegidas con guard de permisos. Nunca `if (user.role === 'admin')` en JSX.
- Sin `any` en TypeScript. Tipado estricto siempre.
- Componentes en PascalCase, hooks en camelCase con prefijo `use`.

---

## 4. Seguridad y datos sensibles

### Cifrado AES-256

| Entidad | Campos cifrados |
|---|---|
| `Usuario` | `email`, `dni`, `cuil`, `cbu`, `alias_cbu` |
| `Comunicacion` | `destinatario` |

Helper en `app/core/crypto.py`. Nunca loguear el valor descifrado. Hay campo hash separado para búsquedas por email — nunca buscar por el campo cifrado directamente.

Test de round-trip obligatorio en cualquier change que toque PII.

### JWT
- Access token: 15 minutos.
- Refresh token: rotación obligatoria — refresh usado se invalida inmediatamente.
- Claims permitidos: `user_id`, `tenant_id`, `roles`, `exp`, `jti`. Sin PII en claims.

### Rate limiting
- 5 intentos / 60s por `IP + email` en login. Configurable via `RATE_LIMIT_LOGIN` en `.env`.

### Secrets
- Todo en `backend/.env` (no commiteado). `.env.example` siempre actualizado sin valores reales.

---

## 5. Flujo de trabajo por change

```
1. LEER
   ├── AGENTS.md (ya en contexto desde el setup)
   ├── CHANGES.md → sección exacta del C-NN
   ├── knowledge-base/ → archivos de "Leer antes"
   └── docs/ARQUITECTURA.md → secciones relevantes

2. IMPLEMENTAR
   ├── Código dentro del scope de CHANGES.md — ni más ni menos
   ├── Migración Alembic si hay modelos nuevos
   ├── Activar la skill correspondiente de la tabla del setup
   └── Tests (coverage ≥ 80% del código nuevo)

3. VERIFICAR
   ├── docker compose up --build      → sin errores
   ├── pytest                         → todos pasan
   ├── ruff check . && ruff format .  → sin errores (backend)
   ├── tsc --noEmit                   → sin errores de tipos (frontend)
   ├── PII ausente en todos los logs
   └── Cada endpoint nuevo tiene guard

4. CERRAR
   ├── Marcar [x] en CHANGES.md
   └── Reportar: "C-NN cerrado. Próximo: C-XX"
```

### Árbol de dependencias — no empezar sin que las deps estén en [x]

```
C-01 → C-02 → C-03 → C-04 ──┬──> C-05
                              ├──> C-06 ──> C-07 ──┬──> C-08
                              │                     ├──> C-09 → C-10 → C-11 → C-12
                              │                     ├──> C-13
                              │                     ├──> C-14
                              │                     ├──> C-15
                              │                     ├──> C-16
                              │                     ├──> C-17
                              │                     ├──> C-18
                              │                     ├──> C-19 (también C-05)
                              │                     └──> C-20
                              └──> C-21 ──> C-22, C-23, C-24
```

---

## 6. Estructura de directorios

### Backend

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, lifespan, middlewares
│   ├── core/
│   │   ├── config.py            # Pydantic Settings desde .env
│   │   ├── crypto.py            # AES-256 encrypt/decrypt
│   │   ├── exceptions.py        # Excepciones de dominio
│   │   ├── logging.py           # Logger estructurado JSON
│   │   └── security.py          # JWT, Argon2id
│   ├── db/
│   │   ├── session.py           # AsyncSession factory, dependency
│   │   ├── base.py              # DeclarativeBase + mixins
│   │   └── migrations/          # Alembic env.py + versions/
│   ├── models/                  # SQLAlchemy ORM (un archivo por entidad)
│   ├── schemas/                 # Pydantic v2 schemas (un archivo por dominio)
│   ├── repositories/            # Data access — scope tenant SIEMPRE activo
│   ├── services/                # Lógica de negocio
│   ├── routers/                 # FastAPI routers (un archivo por épica)
│   ├── integrations/
│   │   └── moodle_ws.py
│   └── workers/
│       └── main.py
├── tests/
│   ├── conftest.py
│   └── test_<dominio>/
├── Dockerfile
├── pyproject.toml
└── .env.example
```

### Frontend (se crea en C-21)

```
frontend/
├── src/
│   ├── lib/
│   │   ├── http.ts              # Axios + interceptor auth/refresh
│   │   └── queryClient.ts
│   ├── features/
│   │   ├── auth/                # C-21
│   │   ├── academico/           # C-22
│   │   ├── coordinacion/        # C-23
│   │   └── finanzas/            # C-24
│   ├── components/
│   │   ├── ui/
│   │   └── layout/
│   ├── hooks/
│   ├── types/
│   └── utils/
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

### Knowledge Base — solo lectura, contratos de dominio

| Archivo | Contenido |
|---|---|
| `02_glosario.md` | Términos del dominio — usar estos nombres en el código |
| `03_actores_y_roles.md` | Roles, permisos, RBAC, impersonación |
| `04_modelo_de_datos.md` | Entidades, campos, relaciones |
| `05_reglas_de_negocio.md` | RN-01…RN-XX — irrompibles |
| `06_funcionalidades.md` | Épicas F-XX |
| `07_flujos_principales.md` | Flujos FL-01…FL-12 paso a paso |
| `08_arquitectura_propuesta.md` | ADRs y decisiones arquitectónicas |
| `10_preguntas_abiertas.md` | PA-XX — bloqueantes, nunca asumir respuesta |

**Si el código contradice la KB → el código está mal.**

---

## 7. Testing — contrato mínimo

### Por tipo de change

**Modelos nuevos:** aislamiento multi-tenant, soft delete, timestamps.

**Endpoints nuevos:** sin permiso → 403, sin sesión → 401, `tenant_id` en body ignorado, happy path.

**PII:** campo no aparece en texto plano en DB, no aparece en respuestas de API, round-trip cifrado correcto.

**Lógica de negocio:** un test por cada RN-XX del dominio.

### Fixtures en `conftest.py`

```python
async_client          # httpx.AsyncClient apuntando a la app de test
test_db               # AsyncSession con rollback por test
tenant_factory        # Crea Tenant con datos únicos
user_factory          # Crea Usuario asociado a un tenant
auth_headers(user)    # Authorization: Bearer <token>
admin_headers         # headers de ADMIN
coordinator_headers   # headers de COORDINADOR
```

---

## 8. Base de datos y migraciones

```bash
alembic revision --autogenerate -m "C-NN: entidades creadas"
alembic upgrade head
alembic downgrade -1
```

- Una migración por change. No acumular.
- Nunca `DROP TABLE` / `DROP COLUMN` — soft delete o renombrar.
- Implementar `downgrade()` siempre.
- Verificar que todos los modelos estén importados en `env.py` antes de autogenerar.

### Mixin base (implementado en C-01)

```python
class BaseMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenant.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)
```

---

## 9. Convenciones de API

```
GET    /api/{dominio}/{recurso}
POST   /api/{dominio}/{recurso}
GET    /api/{dominio}/{recurso}/{id}
PATCH  /api/{dominio}/{recurso}/{id}
DELETE /api/{dominio}/{recurso}/{id}   ← soft delete, devuelve 200
```

### Respuestas

```json
{ "data": {...}, "meta": { "total": 42, "page": 1 } }
{ "ok": true }
{ "detail": "La carrera está inactiva", "code": "RN-CARRERA-INACTIVA" }
{ "detail": "Permiso requerido: estructura:gestionar" }
```

Paginación: `page`, `page_size` (max 100), `order_by`, `order_dir` en todos los listados.

---

## 10. Frontend — reglas SPA

- Tokens en memoria del módulo, nunca en storage del browser.
- Interceptor de response: 401 → refresh → reintenta. Si falla → logout → `/login`.
- Rutas con `<ProtectedRoute permission="modulo:accion">`. Sin permiso → `/unauthorized`.
- Query keys como arrays tipados con `as const`.
- Al implementar cualquier UI: activar skill `frontend-design` y definir token system antes de escribir código.

---

## 11. Worker asíncrono

### Estados de Comunicacion

```
Pendiente ──[worker]──> Enviando ──[ok]──> Enviado  ✓
                                 ──[err <3]──> Pendiente (backoff)
                                 ──[err ≥3]──> Error  ✓
Pendiente ──[cancelar]──> Cancelada  ✓

Si tenant requiere aprobación:
  Nueva comunicación → PendienteAprobacion ──[aprobar]──> Pendiente
```

---

## 12. Integración Moodle WS

Cliente en `backend/app/integrations/moodle_ws.py`.

- Error HTTP de Moodle → `502` con mensaje claro.
- Máx 3 reintentos con backoff exponencial.
- Fallback manual: si Moodle no responde, el usuario sube `.xlsx`/`.csv`. Ambas vías convergen en `VersionPadron`. Usar skill `xlsx` para el procesamiento del fallback.

---

## 13. Audit log

`AuditLog` es **append-only** — sin update ni delete a nivel de app ni de DB.

| Código | Change |
|---|---|
| `LOGIN_EXITOSO` / `LOGIN_FALLIDO` | C-03 |
| `IMPERSONACION_INICIAR` / `FINALIZAR` | C-05 |
| `PADRON_CARGAR` | C-09 |
| `CALIFICACIONES_IMPORTAR` | C-10 |
| `ASIGNACION_MODIFICAR` | C-08 |
| `COMUNICACION_ENVIAR` | C-12 |
| `LIQUIDACION_CERRAR` | C-18 |

Nuevos códigos se agregan a esta tabla antes de usarlos en código.

---

## 14. Multi-tenancy — regla de oro

**Ninguna query puede ejecutarse sin filtrar por `tenant_id`.**

El `BaseRepository` la impone automáticamente. Para queries cross-tenant (solo SUPER_ADMIN del sistema): comentar `# CROSS-TENANT: justificación` y obtener aprobación en review.

### Test de aislamiento — corre en CI en cada PR

```python
async def test_tenant_isolation(tenant_a, tenant_b, test_db):
    item = await repo.create(tenant_id=tenant_a.id, ...)
    result = await repo.get_by_id(id=item.id, tenant_id=tenant_b.id)
    assert result is None
```

---

## 15. Mapa de changes

| # | Change | Estado | Gov | Skill |
|---|---|---|---|---|
| C-01 | foundation-setup | ✅ | BAJO | — |
| C-02 | core-models-y-tenancy | ✅ | CRÍTICO | — |
| C-03 | auth-jwt-2fa | ✅ | CRÍTICO | — |
| C-04 | rbac-permisos-finos | ✅ | CRÍTICO | — |
| C-05 | audit-log | ✅ | CRÍTICO | — |
| C-06 | estructura-academica | ✅ | MEDIO | — |
| **C-07** | **usuarios-y-asignaciones** | **✅** | **CRÍTICO** | — |
| C-08 | equipos-docentes | ⬜ | ALTO | `xlsx` |
| C-09 | padron-ingesta-moodle | ⬜ | MEDIO | `xlsx` |
| C-10 | calificaciones-y-umbral | ⬜ | MEDIO | `xlsx` |
| C-11 | analisis-atrasados-reportes | ⬜ | MEDIO | `pdf` |
| C-12 | comunicaciones-cola-worker | ⬜ | ALTO | — |
| C-13 | encuentros-y-guardias | ⬜ | MEDIO | `xlsx` |
| C-14 | evaluaciones-y-coloquios | ⬜ | MEDIO | — |
| C-15 | avisos-y-acknowledgment | ⬜ | MEDIO | — |
| C-16 | tareas-internas | ⬜ | MEDIO | — |
| C-17 | programas-y-fechas-academicas | ⬜ | BAJO | `pdf`, `docx` |
| C-18 | liquidaciones-y-honorarios | ⬜ | CRÍTICO | `xlsx`, `pdf` |
| C-19 | panel-auditoria-metricas | ⬜ | ALTO | — |
| C-20 | perfil-y-mensajeria-interna | ⬜ | BAJO | — |
| C-21 | frontend-shell-y-auth | ⬜ | BAJO | `frontend-design` |
| C-22 | frontend-academico-docente | ⬜ | BAJO | `frontend-design` |
| C-23 | frontend-coordinacion | ⬜ | BAJO | `frontend-design` |
| C-24 | frontend-finanzas-y-admin | ⬜ | BAJO | `frontend-design` |

**Camino crítico:** `C-07 → C-09 → C-10 → C-11 → C-12` + `C-21 → C-22` en paralelo.

---

## 16. Qué hacer si algo no está claro

**Jerarquía de verdad:**
```
knowledge-base/ > docs/ARQUITECTURA.md > AGENTS.md > CHANGES.md > código
```

**PA-XX (preguntas abiertas):** si el change involucra una → detener, documentar en PR, esperar decisión. Nunca asumir.

**Scope creep:** trabajo extra < 30 LOC → incluir con comentario `# fuera-de-scope-C-NN`. Más de 30 LOC → crear `C-NN-ext` en CHANGES.md primero.

---

## 17. Comandos frecuentes

```bash
# Entorno completo
docker compose up --build

# Solo API
cd backend && uvicorn app.main:app --reload --port 8000

# Worker
cd backend && python -m app.workers.main

# Migraciones
alembic upgrade head
alembic revision --autogenerate -m "C-07: usuario, asignacion"

# Tests
pytest
pytest --cov=app --cov-report=term-missing
pytest tests/test_auth/ -v

# Lint
ruff check . --fix && ruff format .
mypy app/

# Frontend
cd frontend && npm run dev
npm run typecheck && npm run test
```

---

*Actualizado al cierre de C-07. Próximo: C-09.*
*Actualizar la columna Estado cada vez que se cierra un change.*
