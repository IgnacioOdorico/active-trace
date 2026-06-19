## ADDED Requirements

### Requirement: Filtros globales del panel de auditoría
La feature SHALL ofrecer a usuarios con permiso `auditoria:ver` (o `auditoria:ver(propio)`) un conjunto de filtros compartidos —rango de fechas (desde/hasta), materia, usuario y estado de actividad— que aplican a todas las sub-vistas del panel. La carga de datos SHALL realizarse mediante hooks de TanStack Query sobre `apiClient` contra los endpoints `/api/v1/admin/panel/*`, nunca con fetch directo.

#### Scenario: Aplicar filtro de rango de fechas
- **WHEN** el usuario selecciona un rango desde/hasta
- **THEN** la feature propaga `desde` y `hasta` a todas las consultas del panel y re-renderiza las sub-vistas con los datos filtrados

#### Scenario: Filtrar por materia
- **WHEN** el usuario selecciona una materia
- **THEN** la feature agrega `materia_id` a las consultas del panel y muestra solo datos de esa materia

#### Scenario: Alcance reducido para COORDINADOR propio
- **WHEN** el usuario tiene `auditoria:ver(propio)` y el backend retorna datos acotados a sus materias asignadas
- **THEN** la feature renderiza esos datos como resultado normal, sin tratarlos como error ni asumir alcance global

### Requirement: Sub-vista de acciones por día
La feature SHALL mostrar la serie temporal de volumen de acciones consumiendo `GET /api/v1/admin/panel/acciones-por-dia`, respetando los filtros globales.

#### Scenario: Render de acciones por día
- **WHEN** el panel carga con un rango de fechas
- **THEN** la feature llama `GET /api/v1/admin/panel/acciones-por-dia?desde=...&hasta=...` y renderiza el volumen diario ordenado por fecha ascendente

#### Scenario: Sin datos en el rango
- **WHEN** el endpoint responde con lista vacía
- **THEN** la feature muestra un estado informativo sin romper el gráfico

### Requirement: Sub-vista de comunicaciones por docente
La feature SHALL mostrar el estado de comunicaciones agrupado por docente (Pendiente / Enviando / Enviado / Fallido / Cancelado) consumiendo `GET /api/v1/admin/panel/comunicaciones-por-docente`.

#### Scenario: Render de comunicaciones por docente
- **WHEN** el panel carga
- **THEN** la feature llama el endpoint y muestra por docente la distribución de estados de comunicación

### Requirement: Sub-vista de interacciones por docente y materia
La feature SHALL mostrar las métricas de uso por docente y materia consumiendo `GET /api/v1/admin/panel/interacciones-por-docente-materia`, desglosando el total y las acciones por tipo.

#### Scenario: Render de interacciones por docente y materia
- **WHEN** el panel carga
- **THEN** la feature muestra, por combinación docente×materia, el total de acciones y el desglose por tipo

### Requirement: Log de últimas acciones
La feature SHALL mostrar el registro de las últimas acciones consumiendo `GET /api/v1/admin/panel/ultimas-acciones`, con un máximo configurable (por defecto 200), ordenadas por fecha/hora descendente, incluyendo fecha, usuario, materia, tipo de acción, registros afectados, IP y agente de usuario.

#### Scenario: Render del log de últimas acciones
- **WHEN** el panel carga
- **THEN** la feature llama `GET /api/v1/admin/panel/ultimas-acciones?max=200` y renderiza el log ordenado por fecha/hora descendente

#### Scenario: Filtrar log por tipo de acción
- **WHEN** el usuario filtra por un código de acción
- **THEN** la feature agrega `accion=...` a la consulta y muestra solo las entradas de ese tipo

### Requirement: Registro de ruta y menú del panel de auditoría
La feature SHALL registrar su página en `frontend/src/pages/Router.tsx` y agregar el item de menú en la sección "Administración" de `Layout.tsx` con `requiredPermission: 'auditoria:ver'`.

#### Scenario: Menú visible según permiso
- **WHEN** el usuario tiene permiso `auditoria:ver`
- **THEN** el item de menú del panel de auditoría aparece en la sección Administración

#### Scenario: Menú oculto sin permiso
- **WHEN** el usuario no tiene `auditoria:ver` ni `*:*`
- **THEN** el item de menú no se muestra
