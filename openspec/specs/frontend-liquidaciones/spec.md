## ADDED Requirements

### Requirement: Vista de liquidaciones del período con segmentación contable
La feature SHALL mostrar al usuario con permiso `liquidaciones:ver` las liquidaciones de un período seleccionado (cohorte × mes), agrupadas visualmente en tres segmentos según los flags del backend: **General** (`es_nexo=false` y `excluido_por_factura=false`), **NEXO** (`es_nexo=true`) y **Facturantes** (`excluido_por_factura=true`, informativo). Cada fila SHALL mostrar docente, rol, comisiones, monto base, plus y total. La carga SHALL realizarse mediante un hook de TanStack Query sobre `apiClient` llamando `GET /api/v1/liquidaciones?cohorte_id=...&periodo=AAAA-MM`, nunca con fetch directo en el componente. La feature NO SHALL recalcular totales en el cliente.

#### Scenario: Listado segmentado del período
- **WHEN** el usuario selecciona cohorte y mes y la vista carga
- **THEN** la feature llama `GET /api/v1/liquidaciones?cohorte_id=...&periodo=AAAA-MM` y renderiza tres secciones diferenciadas (General, NEXO, Facturantes) con las filas correspondientes a cada flag

#### Scenario: Docentes facturantes mostrados como informativos
- **WHEN** una liquidación tiene `excluido_por_factura=true`
- **THEN** la fila aparece en el segmento Facturantes marcada como informativa y excluida del total de liquidación general

#### Scenario: Estado vacío del período
- **WHEN** el endpoint responde con lista vacía
- **THEN** la feature muestra un estado informativo "sin liquidaciones para el período" sin romper la grilla

#### Scenario: Acceso sin permiso
- **WHEN** el backend responde 403 por falta de `liquidaciones:ver`
- **THEN** la feature muestra un mensaje de acceso denegado y no renderiza datos

### Requirement: KPIs de cabecera por segmento
La feature SHALL mostrar KPIs de cabecera obtenidos de `GET /api/v1/liquidaciones/kpis?periodo=AAAA-MM`, incluyendo "Total sin factura" (general + NEXO) y "Total con factura" (facturas pendientes y abonadas), más la cantidad de docentes por segmento. Los montos mostrados SHALL provenir del endpoint, no de sumas calculadas en el cliente.

#### Scenario: KPIs reflejan los totales del backend
- **WHEN** la vista del período carga
- **THEN** la feature llama `/api/v1/liquidaciones/kpis` y muestra total_general, total_nexo, total_facturas_pendientes y total_facturas_abonadas tal como los retorna el backend

#### Scenario: KPIs se actualizan tras cerrar
- **WHEN** el usuario cierra una liquidación del período
- **THEN** la feature invalida y refresca la query de KPIs para reflejar el estado actualizado

### Requirement: Cerrar liquidación con confirmación e inmutabilidad (RN-22)
La feature SHALL ofrecer la acción "Cerrar liquidación" solo a usuarios con permiso `liquidaciones:cerrar`. La acción SHALL requerir una confirmación explícita que advierta que el cierre es irreversible, y al confirmar SHALL enviar `POST /api/v1/liquidaciones/{id}/cerrar`. Tras un cierre exitoso, la feature SHALL invalidar la query del período y renderizar la liquidación en modo solo-lectura, ocultando la acción de cierre.

#### Scenario: Cierre exitoso de liquidación abierta
- **WHEN** el usuario confirma el cierre de una liquidación en estado Abierta
- **THEN** la feature envía `POST /api/v1/liquidaciones/{id}/cerrar`, refresca el período y muestra la liquidación como Cerrada en solo-lectura

#### Scenario: Confirmación obligatoria antes del cierre
- **WHEN** el usuario hace clic en "Cerrar liquidación"
- **THEN** la feature muestra un diálogo de confirmación que advierte la irreversibilidad y no envía el request hasta que el usuario confirma

#### Scenario: Liquidación ya cerrada no ofrece cierre
- **WHEN** una liquidación está en estado Cerrada
- **THEN** la feature no muestra el botón de cierre y presenta el detalle en modo solo-lectura

#### Scenario: Backend rechaza cierre de liquidación ya cerrada
- **WHEN** el backend responde 409 al intentar cerrar una liquidación ya Cerrada
- **THEN** la feature muestra un mensaje informativo no destructivo y mantiene el estado mostrado

#### Scenario: Cierre sin permiso
- **WHEN** el usuario no tiene `liquidaciones:cerrar`
- **THEN** la feature no muestra la acción de cierre

### Requirement: Detalle individual de liquidación
La feature SHALL permitir abrir la vista previa del detalle individual de una liquidación (base, plus por grupo, total) sin ejecutar ninguna acción irreversible.

#### Scenario: Ver detalle individual
- **WHEN** el usuario abre el detalle de una fila de liquidación
- **THEN** la feature muestra el desglose de monto base, plus por grupo y total de ese docente

### Requirement: Historial de liquidaciones
La feature SHALL permitir consultar liquidaciones de períodos anteriores mediante `GET /api/v1/liquidaciones/historial`, con filtros por rango de períodos (desde/hasta) y estado (Abierta/Cerrada), ordenadas por período descendente.

#### Scenario: Consultar historial por rango
- **WHEN** el usuario selecciona un rango de períodos en la vista de historial
- **THEN** la feature llama `GET /api/v1/liquidaciones/historial?desde=AAAA-MM&hasta=AAAA-MM` y renderiza las liquidaciones ordenadas por período descendente

#### Scenario: Filtrar historial por estado
- **WHEN** el usuario filtra por estado=Cerrada
- **THEN** la feature solicita solo liquidaciones cerradas y muestra únicamente esas

### Requirement: Registro de ruta y menú de Finanzas
La feature SHALL registrar su página en `frontend/src/pages/Router.tsx` bajo el layout protegido y SHALL agregar el item de menú correspondiente en `frontend/src/features/shell/components/Layout.tsx` con `requiredPermission: 'liquidaciones:ver'`, de modo que solo sea visible para roles con ese permiso.

#### Scenario: Menú visible según permiso
- **WHEN** el usuario tiene permiso `liquidaciones:ver`
- **THEN** el item de menú de Liquidaciones aparece en la sección Finanzas

#### Scenario: Menú oculto sin permiso
- **WHEN** el usuario no tiene `liquidaciones:ver` ni `*:*`
- **THEN** el item de menú de Liquidaciones no se muestra
