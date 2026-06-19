## 1. Andamiaje y reconocimiento de contratos

- [x] 1.1 Verificar en el backend las rutas exactas de usuarios del tenant y ABM de carreras/cohortes (resolver Open Question del design); anotar rutas confirmadas
- [x] 1.2 Verificar si existe endpoint de export de planilla de liquidación (`liquidaciones:exportar`) y su ruta; si no existe, dejar el botón preparado y deshabilitado
- [x] 1.3 Confirmar el origen del catálogo de grupos de materia para SalarioPlus (endpoint vs. texto libre)
- [x] 1.4 Crear la estructura de carpetas de las seis features bajo `frontend/src/features/`: `liquidaciones/`, `grilla-salarial/`, `facturas/`, `estructura-academica/`, `usuarios/`, `panel-auditoria/` (cada una con `components/`, `hooks/`, `pages/`, `types.ts`)

## 2. Feature liquidaciones (FINANZAS)

- [x] 2.1 Definir tipos en `liquidaciones/types.ts` (Liquidacion con flags `es_nexo`/`excluido_por_factura`, KpisPeriodo, filtros cohorte/mes/docente, estado Abierta/Cerrada)
- [x] 2.2 Implementar `hooks/useLiquidacionesApi.ts`: `useLiquidaciones` (GET listado), `useKpisPeriodo` (GET /kpis), `useHistorialLiquidaciones` (GET /historial), `useCerrarLiquidacion` (POST /{id}/cerrar con invalidación de listado y KPIs)
- [x] 2.3 Implementar componente de filtros del período (selector de cohorte vía hook de estructura, `<input type="month">` para AAAA-MM, selector opcional de docente)
- [x] 2.4 Implementar componente de KPIs de cabecera ("Total sin factura", "Total con factura", cantidades por segmento) leyendo del endpoint, sin recalcular en cliente
- [x] 2.5 Implementar la grilla segmentada en tres bloques (General / NEXO / Facturantes) agrupando filas por flags; facturantes en modo informativo
- [x] 2.6 Implementar el detalle individual de liquidación (desglose base/plus/total) en modo solo-lectura
- [x] 2.7 Implementar la acción "Cerrar liquidación" con diálogo de confirmación de irreversibilidad (RN-22), render solo-lectura post-cierre, ocultamiento del botón en cerradas y manejo del 409
- [x] 2.8 Implementar la vista de historial con filtros por rango de períodos y estado
- [x] 2.9 Implementar `pages/LiquidacionesPage.tsx` componiendo filtros + KPIs + segmentos + historial, gated por `liquidaciones:ver`

## 3. Feature grilla-salarial (FINANZAS)

- [x] 3.1 Definir tipos en `grilla-salarial/types.ts` (SalarioBase, SalarioPlus, requests de creación/edición)
- [x] 3.2 Crear `grilla-salarial/schemas.ts` con validación Zod (monto positivo, `desde` < `hasta` cuando `hasta` no es nula)
- [x] 3.3 Implementar `hooks/useGrillaSalarialApi.ts`: CRUD de salario-base y salario-plus (`GET/POST/PATCH`) con invalidación de queries
- [x] 3.4 Implementar el ABM de SalarioBase (tabla + formulario RHF, manejo de 422 por solapamiento sin perder formulario)
- [x] 3.5 Implementar el ABM de SalarioPlus (tabla + formulario con grupo, rol, monto, descripción, vigencia)
- [x] 3.6 Implementar `pages/GrillaSalarialPage.tsx` con las dos sub-vistas, gated por `liquidaciones:configurar-salarios` (ocultar acciones y manejar 403)

## 4. Feature facturas (FINANZAS)

- [x] 4.1 Definir tipos en `facturas/types.ts` (Factura, estados Pendiente/Abonada, filtros)
- [x] 4.2 Implementar `hooks/useFacturasApi.ts`: `useFacturas` (GET con filtros), `useCargarFactura` (POST multipart/form-data), `useAbonarFactura` (PATCH /{id}/abonar) con invalidación
- [x] 4.3 Implementar el listado filtrable (docente, estado, período, búsqueda) con estado vacío informativo
- [x] 4.4 Implementar el formulario de carga con validación de PDF en cliente y manejo del 422 del backend
- [x] 4.5 Implementar la acción "Marcar como abonada" con manejo del 409, gated por `facturas:abonar`
- [x] 4.6 Implementar `pages/FacturasPage.tsx` gated por `facturas:ver`

## 5. Feature estructura-academica (ADMIN)

- [x] 5.1 Definir tipos en `estructura-academica/types.ts` (Carrera, Cohorte, Materia, requests)
- [x] 5.2 Crear `estructura-academica/schemas.ts` (carrera: código/nombre requeridos; cohorte: nombre/año/vigencia con `desde` < `hasta`)
- [x] 5.3 Implementar `hooks/useEstructuraApi.ts`: ABM de carreras, cohortes y materias; exponer hooks de catálogo (cohortes/carreras) reutilizables por liquidaciones; reutilizar `useMaterias` de `features/academico` para lecturas compartidas
- [x] 5.4 Implementar el ABM de carreras (listado + alta/edición + cambio de estado)
- [x] 5.5 Implementar el ABM de cohortes (listado + alta/edición + cambio de estado con validación de vigencia)
- [x] 5.6 Implementar el ABM de materias (listado + alta/edición)
- [x] 5.7 Implementar `pages/EstructuraAcademicaPage.tsx` gated por `estructura:gestionar`

## 6. Feature usuarios (ADMIN)

- [x] 6.1 Definir tipos en `usuarios/types.ts` (Usuario del tenant, datos de liquidación/facturación, modalidad de cobro, filtros)
- [x] 6.2 Crear `usuarios/schemas.ts` (campos requeridos según modalidad de cobro factura/liquidación)
- [x] 6.3 Implementar `hooks/useUsuariosApi.ts`: listado con filtros, alta, edición y activación/desactivación con invalidación
- [x] 6.4 Implementar el listado filtrable (rol, estado, búsqueda) con estado vacío
- [x] 6.5 Implementar el formulario de alta/edición con datos de identidad y de liquidación/facturación, manejo de 422
- [x] 6.6 Implementar la acción de activar/desactivar usuario
- [x] 6.7 Implementar `pages/UsuariosPage.tsx` gated por el permiso de gestión de usuarios (ocultar acciones y manejar 403)

## 7. Feature panel-auditoria (ADMIN)

- [x] 7.1 Definir tipos en `panel-auditoria/types.ts` (AccionPorDia, ComunicacionPorDocente, InteraccionDocenteMateria, AuditLogEntry, filtros globales)
- [x] 7.2 Implementar `hooks/usePanelAuditoriaApi.ts`: hooks para `acciones-por-dia`, `comunicaciones-por-docente`, `interacciones-por-docente-materia`, `ultimas-acciones` (todos bajo `/api/v1/admin/panel/*`)
- [x] 7.3 Implementar el componente de filtros globales (rango de fechas, materia, usuario, estado) que propaga a todas las sub-vistas
- [x] 7.4 Implementar la sub-vista de acciones por día (serie temporal) con estado vacío
- [x] 7.5 Implementar la sub-vista de comunicaciones por docente (distribución de estados)
- [x] 7.6 Implementar la sub-vista de interacciones por docente×materia (total + desglose por tipo)
- [x] 7.7 Implementar el log de últimas acciones (max configurable, orden descendente, filtro por tipo de acción)
- [x] 7.8 Implementar `pages/PanelAuditoriaPage.tsx` componiendo filtros + sub-vistas, gated por `auditoria:ver`; tratar alcance reducido `(propio)` como resultado normal

## 8. Integración de rutas y menú

- [x] 8.1 Registrar las rutas nuevas en `frontend/src/pages/Router.tsx` bajo el layout protegido (`/finanzas/liquidaciones`, `/finanzas/grilla-salarial`, `/finanzas/facturas`, `/admin/estructura`, `/admin/usuarios`, `/admin/auditoria`)
- [x] 8.2 Agregar la sección "Finanzas" en `Layout.tsx` con items gated por `liquidaciones:ver`, `liquidaciones:configurar-salarios` y `facturas:ver`
- [x] 8.3 Agregar la sección "Administración" en `Layout.tsx` con items gated por `estructura:gestionar`, permiso de gestión de usuarios y `auditoria:ver`

## 9. Tests de flujos críticos

- [x] 9.1 Test de la vista de liquidación segmentada: renderiza los tres segmentos (General/NEXO/Facturantes) y los KPIs provenientes del endpoint
- [x] 9.2 Test del cierre de liquidación: confirmación obligatoria, POST al confirmar, render solo-lectura post-cierre y manejo del 409
- [x] 9.3 Test del ABM de grilla salarial: alta válida con invalidación, validación de vigencia en cliente y manejo del 422 por solapamiento
- [x] 9.4 Test del panel de auditoría con filtros: propagación de filtros a las sub-vistas y estados vacíos
- [x] 9.5 (Cobertura complementaria) Test de carga de factura: validación de PDF en cliente y cambio de estado a Abonada
