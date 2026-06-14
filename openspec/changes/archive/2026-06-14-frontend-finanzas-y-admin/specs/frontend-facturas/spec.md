## ADDED Requirements

### Requirement: Listado filtrable de facturas
La feature SHALL mostrar a usuarios con permiso `facturas:ver` el listado de comprobantes mediante `GET /api/v1/facturas`, con filtros por docente, estado (Pendiente/Abonada), período y búsqueda libre. La carga SHALL realizarse con un hook de TanStack Query sobre `apiClient`, nunca con fetch directo. Cada fila SHALL mostrar fecha de carga, docente, período, detalle, tamaño del archivo y estado.

#### Scenario: Listar facturas por período
- **WHEN** el usuario filtra por un período
- **THEN** la feature llama `GET /api/v1/facturas?periodo=AAAA-MM` y renderiza solo las facturas de ese período

#### Scenario: Filtrar por estado
- **WHEN** el usuario filtra por estado=Pendiente
- **THEN** la feature solicita solo facturas pendientes y muestra únicamente esas

#### Scenario: Estado vacío
- **WHEN** el endpoint responde con lista vacía
- **THEN** la feature muestra un estado informativo sin romper la tabla

### Requirement: Carga de comprobante PDF
La feature SHALL permitir a usuarios con permiso `facturas:cargar` adjuntar un comprobante PDF junto con docente, período y detalle, enviándolo como `multipart/form-data` a `POST /api/v1/facturas`. La feature SHALL validar en el cliente que el archivo tenga extensión `.pdf` antes de enviar, y SHALL mostrar el error 422 del backend si el archivo es rechazado.

#### Scenario: Carga de PDF válido
- **WHEN** el usuario selecciona un PDF y completa los campos requeridos y confirma
- **THEN** la feature envía `POST /api/v1/facturas` como multipart/form-data, muestra confirmación e invalida la query de facturas

#### Scenario: Rechazo de archivo no PDF en cliente
- **WHEN** el usuario selecciona un archivo que no es PDF
- **THEN** la feature bloquea el envío y muestra un error de validación local

#### Scenario: Rechazo de archivo no PDF en backend
- **WHEN** el backend responde 422 con "El archivo debe ser PDF"
- **THEN** la feature muestra ese mensaje sin perder los datos del formulario

#### Scenario: Carga sin permiso
- **WHEN** el usuario no tiene `facturas:cargar`
- **THEN** la feature no muestra la acción de carga

### Requirement: Cambio de estado Pendiente a Abonada
La feature SHALL permitir a usuarios con permiso `facturas:abonar` marcar una factura pendiente como abonada mediante `PATCH /api/v1/facturas/{id}/abonar`, invalidando la query del listado tras el éxito.

#### Scenario: Abonar factura pendiente
- **WHEN** el usuario marca como abonada una factura en estado Pendiente
- **THEN** la feature envía `PATCH /api/v1/facturas/{id}/abonar`, refresca el listado y la factura aparece como Abonada

#### Scenario: Abonar factura ya abonada
- **WHEN** el backend responde 409 al intentar abonar una factura ya Abonada
- **THEN** la feature muestra un mensaje informativo no destructivo y mantiene el estado mostrado

#### Scenario: Acción de abono oculta sin permiso
- **WHEN** el usuario no tiene `facturas:abonar`
- **THEN** la feature no muestra la acción de marcar como abonada
