## Why

El backend de los dominios de coordinación (equipos docentes, avisos, tareas internas, encuentros, coloquios, programas y fechas académicas) ya está implementado y verificado (C-08, C-13, C-14, C-15, C-16, C-17), y el shell SPA con auth, guards por permiso y cliente HTTP con refresh transparente está en producción (C-21). Hoy el COORDINADOR y el ADMIN no tienen ninguna interfaz para operar esos dominios: el setup de cuatrimestre, la publicación de avisos y el workflow de tareas se quedan sin capa de presentación. Este change construye las features de frontend que cierran esa brecha y habilitan el flujo FL-03 (setup de inicio de cuatrimestre) de punta a punta.

## What Changes

- **Gestión de equipos docentes** (Épica 4): vista "mis equipos" con filtros, gestión de asignaciones, asignación masiva (bloque docentes × materia × carrera × cohorte × rol), clonado de equipo entre períodos, modificación de vigencia individual y en bloque, y exportación. Consume `/api/equipos/*`.
- **Tablón de avisos** (F3.5, FL-09): ABM de avisos con configuración de alcance (global / materia / cohorte / rol), severidad, vigencia, orden, requiere_ack; vista de gestión con contadores de acknowledgment. Consume `/api/avisos/*`.
- **Tareas internas** (Épica 8, FL-05): vista "mis tareas", administración global con filtros (asignado/asignador/materia/estado/búsqueda), transiciones de estado y comentarios en hilo (workflow asincrónico). Consume `/api/tareas/*`.
- **Monitores transversales** (F2.7, F2.9): monitor general del tenant y monitor de seguimiento coordinación/admin con filtros extendidos (incluye rango de fechas). Reutiliza el feature `monitor-seguimiento` existente, agregando las vistas/permisos de coordinación.
- **Encuentros (vista admin)** (F6.5, FL-06): vista transversal de todos los encuentros del tenant para supervisión; registro y consulta global de guardias con export. Consume `/api/encuentros/*`, `/api/guardias/*`.
- **Coloquios** (Épica 7, FL-07): panel de métricas, creación de convocatoria, importación de alumnos, listado de convocatorias y administración global. Consume `/api/coloquios/*`.
- **Setup de cuatrimestre** (FL-03): página guía/orquestadora que encadena cohorte → clonar equipo → ajuste de asignaciones → vigencias → programas → fechas → aviso de bienvenida; consume `/api/programas/*` y `/api/fechas-academicas/*`.
- **Navegación**: nueva sección "Coordinación" en el menú del shell, con ítems protegidos por permiso (`equipos:asignar`, `avisos:publicar`, `tareas:gestionar`, `encuentros:gestionar`), y registro de rutas en el `AppRouter`.
- **Tests** de componentes/integración con mocks: ABM equipos, clonado, publicación de aviso, workflow de tarea, filtros de monitor.

No hay cambios de backend ni de contrato de API: este change solo agrega capa de presentación que consume endpoints existentes.

## Capabilities

### New Capabilities
- `frontend-equipos-coordinacion`: UI de gestión de equipos docentes (mis-equipos, asignación masiva, clonado, vigencia individual/masiva, export) sobre `/api/equipos/*`.
- `frontend-avisos`: UI de ABM de avisos con scope/severidad/vigencia/orden/ack y contadores de acknowledgment sobre `/api/avisos/*`.
- `frontend-tareas`: UI de tareas internas (mis tareas, administración global, workflow de estados, comentarios en hilo) sobre `/api/tareas/*`.
- `frontend-monitores-coordinacion`: UI de monitores transversales general (F2.7) y de seguimiento coordinación/admin con rango de fechas (F2.9) sobre `/api/analisis/*`.
- `frontend-encuentros-admin`: UI de vista transversal de encuentros y registro/consulta global de guardias sobre `/api/encuentros/*` y `/api/guardias/*`.
- `frontend-coloquios`: UI de coloquios (métricas, convocatorias, importación de alumnos, listado, administración) sobre `/api/coloquios/*`.
- `frontend-setup-cuatrimestre`: UI orquestadora del flujo FL-03 que encadena los pasos de inicio de período sobre `/api/programas/*`, `/api/fechas-academicas/*` y los endpoints de equipos/avisos.

### Modified Capabilities
<!-- No se modifican requisitos de specs existentes. Las capabilities de backend (equipos-docentes, avisos, tareas, etc.) no cambian su contrato; este change solo agrega features de frontend que las consumen. -->

## Impact

- **Frontend (nuevo código)**: `frontend/src/features/{equipos,avisos,tareas,encuentros-admin,coloquios,setup-cuatrimestre}/` con la estructura `{components,hooks,pages,types}`. Ampliación del feature `monitor-seguimiento` para las vistas de coordinación.
- **Frontend (modificado)**: `frontend/src/features/shell/components/Layout.tsx` (nueva sección "Coordinación" en el menú) y `frontend/src/pages/Router.tsx` (registro de rutas protegidas).
- **Cliente HTTP**: reutiliza `frontend/src/shared/services/httpClient.ts` (refresh transparente + manejo 401/403) sin cambios.
- **Backend**: sin cambios. Se consumen endpoints ya implementados de C-08, C-13, C-14, C-15, C-16, C-17.
- **Permisos**: las features se guardan por `equipos:asignar`, `avisos:publicar`, `tareas:gestionar`, `encuentros:gestionar`, `monitores:ver` / `atrasados:ver` según el endpoint; el guard de UI replica el server-side (defensa en profundidad, la autorización real es del backend).
