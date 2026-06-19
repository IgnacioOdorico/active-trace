## Context

El shell SPA (C-21) ya provee: scaffolding React 18 + TypeScript + Vite, estructura feature-based, Tailwind, TanStack Query, React Hook Form + Zod, cliente HTTP centralizado (`shared/services/httpClient.ts`) con interceptor de auth y refresh transparente, guard de rutas (`ProtectedRoute`), y `Layout` con menú filtrado por permisos de la sesión (`user.permissions`, soportando wildcard `*:*`). C-22 ya estableció el patrón concreto de features (`calificaciones-importar`, `monitor-seguimiento`, etc.): cada feature en `features/<name>/{components,hooks,pages,types}`, con un hook `use<Feature>Api` que envuelve `useQuery`/`useMutation` de TanStack Query sobre `apiClient`.

El backend de todos los dominios consumidos está implementado y verificado, con estos prefijos de router confirmados:
- `/api/equipos` — mis-equipos, asignacion-masiva, clonar, `{id}/vigencia`, vigencia-masiva, `{id}/exportar`.
- `/api/avisos` — POST/GET/`gestion`/`{id}` GET-PATCH-DELETE/`{id}/ack`.
- `/api/tareas` — POST, `mias`, GET (admin), `{id}` GET-PATCH-DELETE, `{id}/comentarios` GET-POST.
- `/api/encuentros` — `slots`, `instancias` (POST/GET), `instancias/{id}` PATCH, `html/{materia_id}`.
- `/api/guardias` — POST, GET, `{id}` PATCH, `exportar`.
- `/api/coloquios` — `metricas`, POST, GET, `{id}` GET-PATCH, `{id}/cerrar`, `{id}/alumnos`, `{id}/resultados`, `{id}/metricas`, `{id}/agenda`.
- `/api/fechas-academicas` — POST/GET/`{id}` GET-PATCH-DELETE/`lms/{materia}/{cohorte}`.
- `/api/programas` — POST/GET/`{id}` GET-PATCH-DELETE.

Este change es la capa de presentación: NO toca backend ni contratos.

## Goals / Non-Goals

**Goals:**
- Entregar las features de COORDINADOR/ADMIN consumiendo los endpoints existentes, siguiendo exactamente el patrón de C-22.
- Habilitar el flujo FL-03 (setup de cuatrimestre) de punta a punta desde una página orquestadora.
- Mantener defensa en profundidad: el guard de UI por permiso replica el guard server-side, pero la autorización real sigue siendo del backend.
- Tests de componentes/integración con mocks de `apiClient` para los flujos clave.

**Non-Goals:**
- Modificar contratos de API o agregar endpoints (cualquier gap se reporta como blocker, no se implementa backend acá).
- Reescribir el feature `monitor-seguimiento` de C-22: solo se extiende para las vistas de coordinación (F2.9 con rango de fechas).
- Features de PROFESOR ya cubiertas por C-22 (importación, atrasados, comunicaciones).
- Funcionalidades de ALUMNO (reserva de coloquio FL-07 paso 4): este change cubre la cara de gestión COORDINADOR/ADMIN, no la reserva del alumno.
- Editor de texto enriquecido custom: el cuerpo del aviso se maneja como textarea (formato enriquecido es nice-to-have fuera de scope).

## Decisions

### D1 — Una feature por capability, espejando los routers de backend
Cada capability del proposal mapea a una carpeta `features/<name>/`. Esto mantiene la cohesión screaming-architecture ya establecida en C-22 y evita features monolíticas.
- **Alternativa descartada**: una sola feature "coordinacion" con todo adentro → violaría el límite de cohesión y los componentes < 200 LOC, y mezclaría dominios sin relación (equipos vs coloquios).

### D2 — Hooks `use<Feature>Api` con TanStack Query, nunca fetch en componentes
Se sigue el patrón de `useMonitoresApi`/`useComunicacionesApi`: `useQuery` para lecturas con `queryKey: ['<dominio>', filtros]`, `useMutation` con `invalidateQueries` para escrituras. Todo fetch pasa por `apiClient` (`httpClient.ts`), nunca axios/fetch directo en componentes.
- **Rationale**: refresh transparente, manejo 401/403 y baseURL ya viven en `httpClient`; reusarlo es obligatorio.

### D3 — `setup-cuatrimestre` es una página orquestadora, no un wizard con estado de servidor propio
La página FL-03 es un stepper de UI que reutiliza los hooks de las features de equipos/avisos/programas/fechas. No mantiene estado persistente propio: cada paso dispara el endpoint del dominio correspondiente y muestra el progreso. Permite saltar pasos (no todos son obligatorios en cada período).
- **Alternativa descartada**: un endpoint de backend "setup" transaccional → no existe en backend y crearlo está fuera de scope; además FL-03 es inherentemente un flujo guiado de pasos independientes.

### D4 — Navegación: nueva sección "Coordinación" en `Layout`, ítems con `requiredPermission`
Se agrega una `MenuSection` "Coordinación" al array `menuSections` de `Layout.tsx`. Cada ítem declara su `requiredPermission` y el filtro existente (`perms.includes('*:*') || perms.includes(req)`) lo oculta si la sesión no lo tiene. Rutas se registran en `pages/Router.tsx` bajo el `Layout` protegido.
- **Rationale**: reusa el mecanismo de visibilidad por permiso ya probado en C-21/C-22; no se inventa un nuevo sistema de menú.

### D5 — Validación de formularios con React Hook Form + Zod
Avisos (alcance/severidad/vigencia/ack), asignación masiva, clonado, convocatoria de coloquio y tarea usan RHF + esquemas Zod en `schemas.ts` por feature (patrón de `gestion-umbral/schemas.ts`). La validación de fechas (vigencia inicio < fin) y de scope condicional (materia/cohorte requeridas si alcance no es global) vive en el schema.

### D6 — Tipos derivados de las respuestas reales del backend
Cada feature define `types.ts` con interfaces TypeScript que reflejan los `response_model` del router correspondiente (sin `any`). Donde el backend devuelve `dict` genérico, se tipa explícitamente según el schema Pydantic del endpoint.

### D7 — Reutilización del feature `monitor-seguimiento` existente
F2.7 (monitor general) y F2.9 (seguimiento coordinación con rango de fechas) ya tienen hooks (`useMonitorGeneral`, `useMonitorSeguimiento` con `fecha_desde`/`fecha_hasta`) y componentes en C-22. Para coordinación se agrega la entrada de menú con permiso de coordinación y, si hace falta, un wrapper de página; no se duplica la lógica de fetch.

## Risks / Trade-offs

- **[Drift entre tipos TS y schemas Pydantic del backend]** → Mitigación: derivar `types.ts` leyendo los `*Response` reales de cada router al implementar; los tests de integración con mocks fijan la forma esperada.
- **[Endpoints `dict` genéricos sin schema fuerte]** (varios PATCH/POST de coloquios, encuentros, fechas, programas devuelven `response_model=dict`) → Mitigación: inspeccionar el service/schema correspondiente al implementar cada hook y tipar la respuesta; documentar en el type cuál es la forma asumida.
- **[FL-03 sin transacción atómica de backend]** → Mitigación: la página orquestadora deja claro qué pasos se completaron y permite reintentar pasos individuales; no promete atomicidad.
- **[Gap de endpoint inesperado]** (p.ej. falta un export, o un filtro del monitor no soportado) → Mitigación: si al implementar aparece un endpoint faltante, se reporta como blocker y se marca la task como bloqueada, sin implementar backend en este change.
- **[Permisos de UI desincronizados del backend]** → Mitigación: el guard de UI es solo UX; un 403 del backend se maneja en `httpClient`. La fuente de verdad de autorización es el server.

## Migration Plan

No hay migración de datos ni de schema (cambio 100% frontend). Despliegue: build del SPA estático sobre el shell existente. Rollback: revertir el bundle a la versión previa; no hay estado persistente nuevo. Las features se activan por permiso, así que usuarios sin los permisos de coordinación no ven cambios.

## Open Questions

- ¿El backend expone un endpoint de listado de docentes asignables / catálogo de carreras-cohortes-materias para poblar los selects de asignación masiva y clonado, o se reutilizan los endpoints de C-06/C-07 (`/api/admin/*`, `/api/asignaciones`)? Se asume reutilización de esos endpoints; confirmar al implementar.
- ¿La forma exacta de los `response_model=dict` de coloquios/encuentros/fechas se documenta en algún schema, o hay que inferirla del service? Se inspecciona al implementar cada hook.
