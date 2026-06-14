## Why

El backend de liquidaciones (C-18), estructura académica (C-06), usuarios (C-07) y auditoría (C-19) ya está implementado y especificado, pero el rol FINANZAS y las tareas de administración del tenant todavía no tienen interfaz en la SPA. Hoy un usuario FINANZAS no puede ver, segmentar ni cerrar liquidaciones, ni gestionar la grilla salarial o las facturas; y un ADMIN no puede administrar carreras/cohortes/materias, usuarios del tenant ni supervisar la auditoría desde el frontend. Este change (C-24) cierra el último gran bloque funcional del frontend conectando esas capacidades de backend a la UI.

## What Changes

- Nueva área **FINANZAS** en la SPA:
  - Vista de liquidaciones del período con segmentación contable en 3 bloques (General / NEXO / Facturantes) y KPIs de cabecera ("Total sin factura", "Total con factura"), filtrable por cohorte, mes y docente.
  - Acción de **cerrar liquidación** que inmutabiliza el período (RN-22) con confirmación explícita; una liquidación cerrada se renderiza en modo solo-lectura y sin acción de cierre.
  - **Historial** de liquidaciones de períodos anteriores (abiertas y cerradas), filtrable por rango de períodos y estado.
  - **Grilla salarial**: ABM de SalarioBase (por rol) y SalarioPlus (por grupo × rol) con vigencia temporal.
  - **Gestión de facturas**: listado filtrable (docente, estado, período), carga de comprobante PDF y cambio de estado Pendiente → Abonada.
- Nueva área **ADMIN** en la SPA:
  - **Estructura académica**: ABM de carreras, cohortes y materias del tenant.
  - **Usuarios del tenant**: listado y ABM de usuarios docentes (alta, edición, activación/desactivación, datos de liquidación/facturación).
  - **Panel de auditoría y métricas**: acciones por día, comunicaciones por docente, interacciones por docente×materia y log de últimas acciones, con filtros de rango de fechas, materia, usuario y estado.
- Registro de nuevas rutas en `pages/Router.tsx` y nuevas secciones de menú ("Finanzas", "Administración") en `Layout.tsx`, visibles según permisos.
- Cobertura de tests para los flujos críticos: liquidación segmentada, cierre inmutable, ABM de grilla salarial y panel de auditoría con filtros.

Nota: este change es exclusivamente de **frontend**. No modifica contratos de backend ni el comportamiento de los endpoints ya especificados; solo los consume.

## Capabilities

### New Capabilities
- `frontend-liquidaciones`: vista segmentada de liquidaciones del período con KPIs, cierre inmutable (RN-22) e historial, consumiendo los endpoints de cálculo, listado, KPIs, cierre e historial.
- `frontend-grilla-salarial`: ABM de SalarioBase y SalarioPlus con vigencia temporal, gobernado por el permiso `liquidaciones:configurar-salarios`.
- `frontend-facturas`: gestión de comprobantes de docentes facturantes (listado filtrable, carga de PDF y cambio de estado Pendiente/Abonada).
- `frontend-estructura-academica`: ABM de carreras, cohortes y materias del tenant para el rol ADMIN.
- `frontend-usuarios-tenant`: listado y ABM de usuarios docentes del tenant (alta, edición, activación/desactivación, datos de liquidación y facturación).
- `frontend-panel-auditoria`: panel de auditoría y métricas de uso (acciones por día, comunicaciones por docente, interacciones por docente×materia, log de últimas acciones) con filtros.

### Modified Capabilities
<!-- Ninguna. Este change solo agrega UI sobre contratos de backend ya especificados; no cambia requisitos de specs existentes. -->

## Impact

- **Código nuevo (frontend)**: nuevos directorios feature-based bajo `frontend/src/features/` — `liquidaciones/`, `grilla-salarial/`, `facturas/`, `estructura-academica/`, `usuarios/`, `panel-auditoria/` (cada uno con `components/`, `hooks/`, `pages/`, `types.ts`, y `schemas.ts` donde haya formularios).
- **Código modificado (frontend)**: `frontend/src/pages/Router.tsx` (nuevas rutas) y `frontend/src/features/shell/components/Layout.tsx` (nuevas secciones de menú según permisos).
- **APIs consumidas (sin cambios)**: `liquidaciones:*` (`GET/POST /api/v1/liquidaciones`, `/kpis`, `/historial`, `/{id}/cerrar`), grilla salarial (`/api/v1/salario-base`, `/api/v1/salario-plus`), facturas (`/api/v1/facturas`, `/{id}/abonar`), estructura (`/api/v1/estructura/*`), usuarios del tenant y panel de auditoría (`/api/v1/admin/panel/*`).
- **Permisos relevantes**: `liquidaciones:ver`, `liquidaciones:cerrar`, `liquidaciones:configurar-salarios`, `facturas:ver|cargar|abonar`, `estructura:gestionar`, gestión de usuarios y `auditoria:ver` / `auditoria:ver(propio)`.
- **Dependencias**: requiere C-21 (frontend-shell-y-auth), C-18 (liquidaciones-y-honorarios), C-19 (panel-auditoria-metricas) y los backends de C-06 y C-07, todos completos.
- **Sin impacto en backend, base de datos, ni en otras features de frontend** salvo los dos archivos compartidos mencionados (Router y Layout).
