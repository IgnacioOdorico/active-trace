## Context

El frontend de active-trace es una SPA React 18 + TypeScript con Vite, organizada feature-based bajo `frontend/src/features/{name}/{components,hooks,pages,types}`. Las features existentes (C-21 shell/auth, C-22 importación/atrasados/comunicaciones, C-23 equipos/avisos/tareas/etc.) ya establecieron las convenciones que este change debe seguir literalmente:

- Cliente HTTP centralizado en `frontend/src/shared/services/httpClient.ts` (instancia axios `apiClient`). Ningún componente hace `fetch` directo.
- Hooks de datos con patrón `use<Feature>Api` sobre TanStack Query (`useQuery` para lecturas, `useMutation` con `invalidateQueries` para escrituras). Ejemplo de referencia: `frontend/src/features/equipos/hooks/useEquiposApi.ts`.
- Formularios con React Hook Form + Zod (`schemas.ts` por feature).
- Estilos con Tailwind, componentes React < 200 LOC.
- Rutas en `frontend/src/pages/Router.tsx` bajo el layout protegido `/`.
- Menú lateral en `frontend/src/features/shell/components/Layout.tsx`, declarativo: secciones con `requiredPermission`; el Layout ya filtra por `user.permissions` (incluye soporte `*:*`).

Los contratos de backend que se consumen ya están especificados en `openspec/specs/`: `liquidacion`, `grilla-salarial`, `factura`, `separacion-contable`, `panel-interacciones-sistema`, `programas-materia`, `fechas-academicas` y los modelos de auditoría. Este change no los modifica.

## Goals / Non-Goals

**Goals:**
- Conectar a la UI las capacidades de FINANZAS (liquidaciones segmentadas + KPIs, cierre inmutable, historial, grilla salarial, facturas) y ADMIN (estructura académica, usuarios del tenant, panel de auditoría).
- Reutilizar 1:1 los patrones de las features ya implementadas (hooks `use*Api`, `apiClient`, RHF+Zod, Tailwind).
- Hacer visible cada nueva área solo a los roles/permisos correctos, vía el filtrado de menú existente en `Layout.tsx`.
- Hacer del cierre de liquidación una acción consciente e irreversible en la UI (confirmación + render solo-lectura post-cierre), reflejando RN-22.
- Cubrir con tests los 4 flujos críticos indicados: liquidación segmentada, cierre, ABM grilla salarial, panel de auditoría con filtros.

**Non-Goals:**
- No se modifica ningún endpoint, modelo ni regla de negocio de backend.
- No se implementa lógica de cálculo de liquidación en el cliente: el frontend solo presenta lo que el backend computa.
- No se crea un sistema de diseño nuevo ni librerías de UI; se usa Tailwind y los patrones ya presentes.
- No se aborda corrección asistida por IA (Épica 12) ni features de otras épicas fuera del scope FINANZAS/ADMIN.
- No se implementa caché offline ni paginación infinita; se usa el comportamiento por defecto de TanStack Query.

## Decisions

### D1 — Seis features independientes en vez de dos "mega-features"
Aunque el scope se agrupa en FINANZAS y ADMIN, se crean seis features atómicas (`liquidaciones`, `grilla-salarial`, `facturas`, `estructura-academica`, `usuarios`, `panel-auditoria`), una por capability del proposal.
**Por qué**: mantiene cada hook `use*Api` cohesionado con su dominio de backend, evita archivos `types.ts` gigantes y respeta el límite de < 200 LOC por componente. Alternativa descartada: dos features `finanzas/` y `admin/` con subcarpetas — concentraría demasiada superficie y dificultaría los tests focalizados.

### D2 — La segmentación contable se resuelve con datos del backend, no en el cliente
La vista de liquidaciones consume `GET /api/v1/liquidaciones` (lista con flags `es_nexo` / `excluido_por_factura`) y `GET /api/v1/liquidaciones/kpis` (totales por segmento). La UI agrupa visualmente en General / NEXO / Facturantes a partir de esos flags, pero los **totales y KPIs vienen del backend** (separacion-contable spec).
**Por qué**: RN-36/RN-38 son reglas contables; recalcular sumas en el cliente arriesga divergencias con el backend. El cliente solo agrupa filas por flag para presentación. Alternativa descartada: sumar montos en el cliente — duplicaría lógica de negocio y rompería la fuente única de verdad.

### D3 — Cierre de liquidación: confirmación explícita + bloqueo de UI post-cierre
La acción "Cerrar liquidación" abre un diálogo de confirmación que advierte la irreversibilidad (RN-22). Tras `POST /api/v1/liquidaciones/{id}/cerrar`, la mutación invalida la query del período; la vista re-renderiza el período como cerrado, ocultando el botón de cierre y mostrando el detalle en solo-lectura. Un 409 del backend (ya cerrada) se muestra como mensaje no destructivo.
**Por qué**: el cierre es irreversible a nivel de dominio; la UI debe evitar el clic accidental y reflejar el estado inmutable. Alternativa descartada: cierre directo sin confirmación — inaceptable para una acción irreversible.

### D4 — Grilla salarial: dos sub-vistas (Base / Plus) bajo una página, gated por `liquidaciones:configurar-salarios`
`SalarioBase` (rol × monto × vigencia) y `SalarioPlus` (grupo × rol × monto × vigencia) se gestionan en una página con dos tablas/tabs. Validación de vigencia con Zod (`desde` < `hasta` cuando `hasta` no es nula). El solapamiento temporal lo valida el backend (422); la UI muestra ese error sin perder el formulario.
**Por qué**: ambas tablas comparten el concepto de vigencia y permiso; agruparlas reduce navegación. La validación dura de solapamiento queda en backend (fuente de verdad), la UI solo hace validación de forma.

### D5 — Carga de factura como multipart/form-data; descargas/exports como blob
La carga de comprobante (`POST /api/v1/facturas`) usa `FormData` con el PDF, validando en cliente extensión `.pdf` antes de enviar (el backend reconfirma con 422). Los exports de liquidación se manejan con `responseType: 'blob'` siguiendo el patrón de `useExportarEquipo` en `useEquiposApi.ts`.
**Por qué**: consistencia con el patrón de descarga ya existente; la validación temprana de PDF mejora UX sin reemplazar la validación de backend.

### D6 — Reutilización de selectores de cohorte/materia
Las vistas de FINANZAS y ADMIN necesitan selección de cohorte, mes y materia. Se reutiliza el hook `useMaterias` de `features/academico` y se agregan hooks de cohortes/carreras en `features/estructura-academica`. El selector de mes es un input `<input type="month">` mapeado al formato `AAAA-MM` que esperan los endpoints.
**Por qué**: evita duplicar la obtención de catálogos; `academico/useMaterias` ya existe y apunta a `/api/v1/estructura/materias`.

### D7 — Permisos de menú y rutas alineados al RBAC de backend
Se agregan dos secciones de menú en `Layout.tsx`: "Finanzas" (items gated por `liquidaciones:ver`, `liquidaciones:configurar-salarios`, `facturas:ver`) y "Administración" (gated por `estructura:gestionar`, gestión de usuarios y `auditoria:ver`). Las rutas se montan bajo `/finanzas/*` y `/admin/*` dentro del layout protegido existente.
**Por qué**: el Layout ya filtra por `requiredPermission`; basta declarar los items. El gating de UI es defensa en profundidad — el backend sigue siendo la autoridad (403).

## Risks / Trade-offs

- **[Divergencia de KPIs cliente vs backend]** → Mitigación: D2, la UI nunca recalcula totales; muestra los del endpoint `/kpis`.
- **[Cierre accidental e irreversible]** → Mitigación: D3, confirmación explícita + manejo idempotente del 409.
- **[Permiso `auditoria:ver(propio)` con alcance reducido]** → el panel para COORDINADOR ve solo sus materias asignadas; la UI debe tratar resultados acotados como normales, no como error. Mitigación: estados vacíos informativos, sin asumir alcance global.
- **[Contrato de endpoints de usuarios/estructura no detallado en este change]** → algunos endpoints de ADMIN (usuarios del tenant, ABM carreras/cohortes) se infieren de C-06/C-07. Mitigación: ver Open Questions; los hooks se construyen contra `/api/v1/estructura/*` y el módulo de usuarios, verificando rutas exactas al implementar.
- **[Crecimiento de Router.tsx y Layout.tsx]** → ambos archivos crecen con ~10 rutas/items nuevos. Aceptable; siguen el patrón declarativo existente y no superan límites de complejidad.

## Migration Plan

No hay migración de datos ni de backend. El despliegue es aditivo en frontend:
1. Crear las seis features con sus hooks/types/components/pages.
2. Registrar rutas en `Router.tsx` y secciones de menú en `Layout.tsx`.
3. Añadir tests de los flujos críticos.
4. Rollback: revertir el commit del frontend; al ser puramente aditivo y gated por permisos, no afecta features existentes.

## Open Questions

- **Rutas exactas de usuarios del tenant y ABM de carreras/cohortes**: ¿los endpoints viven bajo `/api/v1/estructura/carreras`, `/api/v1/estructura/cohortes` y un módulo de usuarios (`/api/v1/usuarios` o `/api/v1/admin/usuarios`)? Se confirmará leyendo los routers de backend de C-06/C-07 durante apply.
- **Export de liquidación**: ¿el backend expone un endpoint de export (planilla) además de `/kpis` y listado? FL-08 lo menciona (`liquidaciones:exportar`); confirmar ruta exacta. Si no existe aún, el botón de export se deja preparado pero deshabilitado.
- **Grupos de materia para SalarioPlus**: ¿el catálogo de grupos (ej. "PROG", "BD") viene de un endpoint o se ingresa libre? Si no hay endpoint de catálogo, el campo `grupo` se ingresa como texto validado.
