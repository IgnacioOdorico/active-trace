## ADDED Requirements

### Requirement: El sistema SHALL modelar Factura con estados Pendiente y Abonada (RN-39)
`Factura` representa el documento de cobro para docentes que facturan. Campos: usuario, período, detalle, referencia_archivo, tamano_kb, estado (Pendiente|Abonada), fechas de carga y abono.

#### Scenario: Crear factura pendiente
- **WHEN** se carga una factura PDF para el docente X en período 2026-06
- **THEN** el sistema crea Factura con estado=Pendiente y cargada_at=now

#### Scenario: Factura creada con referencia al archivo y tamaño
- **WHEN** se carga un PDF de 150 KB
- **THEN** la factura almacena referencia_archivo con la ruta y tamano_kb=150

### Requirement: El sistema SHALL aceptar carga de factura PDF con `facturas:cargar`
El endpoint POST /api/v1/facturas acepta multipart/form-data con archivo PDF, detalle y período. Almacena el PDF en sistema de archivos y crea el registro en DB.

#### Scenario: Cargar factura PDF válida
- **WHEN** se envía POST /api/v1/facturas con archivo PDF válido, detalle y período
- **AND** el usuario tiene permiso `facturas:cargar`
- **THEN** el sistema retorna 201 con la factura creada en estado Pendiente

#### Scenario: Cargar factura sin permiso retorna 403
- **WHEN** se envía POST /api/v1/facturas sin permiso `facturas:cargar`
- **THEN** el sistema retorna 403

#### Scenario: Cargar archivo no PDF retorna 422
- **WHEN** se envía POST /api/v1/facturas con archivo .docx o .png
- **THEN** el sistema retorna 422 con mensaje "El archivo debe ser PDF"

#### Scenario: Cargar factura sin archivo retorna 422
- **WHEN** se envía POST /api/v1/facturas sin adjuntar archivo
- **THEN** el sistema retorna 422

### Requirement: El sistema SHALL abonar una factura cambiando su estado a Abonada con `facturas:abonar`
El endpoint PATCH /api/v1/facturas/{id}/abonar cambia el estado a Abonada y registra la fecha de abono.

#### Scenario: Abonar factura pendiente
- **WHEN** se envía PATCH /api/v1/facturas/{id}/abonar
- **AND** el usuario tiene permiso `facturas:abonar`
- **AND** la factura está en estado Pendiente
- **THEN** el sistema cambia estado a Abonada y setea abonada_at=now

#### Scenario: Abonar factura ya abonada retorna 409
- **WHEN** se envía PATCH /api/v1/facturas/{id}/abonar sobre una factura ya Abonada
- **THEN** el sistema retorna 409

#### Scenario: Abonar sin permiso retorna 403
- **WHEN** se envía PATCH /api/v1/facturas/{id}/abonar sin permiso `facturas:abonar`
- **THEN** el sistema retorna 403

### Requirement: El sistema SHALL listar facturas filtradas por período y estado
Usuarios con `facturas:ver` pueden consultar facturas.

#### Scenario: Listar facturas por período
- **WHEN** se envía GET /api/v1/facturas?periodo=2026-06
- **AND** el usuario tiene permiso `facturas:ver`
- **THEN** el sistema retorna 200 con lista de facturas de ese período

#### Scenario: Listar facturas por estado
- **WHEN** se envía GET /api/v1/facturas?estado=Pendiente
- **THEN** el sistema retorna solo facturas Pendientes

### Requirement: Las acciones sobre facturas SHALL generar auditoría
Cada carga o abono de factura genera un registro de auditoría.

#### Scenario: Cargar factura genera audit
- **WHEN** se carga una factura
- **THEN** el sistema registra audit con accion="FACTURA_CARGAR"

#### Scenario: Abonar factura genera audit
- **WHEN** se abona una factura
- **THEN** el sistema registra audit con accion="FACTURA_ABONAR"
