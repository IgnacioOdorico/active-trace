## ADDED Requirements

### Requirement: Listado de usuarios del tenant
La feature SHALL mostrar al ADMIN el listado de usuarios docentes del tenant (PROFESOR, TUTOR, NEXO, COORDINADOR) mediante un hook de TanStack Query sobre `apiClient`, con filtros por rol, estado de actividad y búsqueda libre. Cada fila SHALL mostrar nombre, identificación fiscal, rol, regional y estado.

#### Scenario: Listar usuarios con filtros
- **WHEN** el ADMIN aplica un filtro de rol
- **THEN** la feature solicita los usuarios filtrados y renderiza solo los que coinciden

#### Scenario: Estado vacío
- **WHEN** el endpoint responde con lista vacía
- **THEN** la feature muestra un estado informativo sin romper la tabla

### Requirement: Alta y edición de usuario
La feature SHALL permitir al ADMIN crear y editar usuarios con datos de identidad (nombre, identificación fiscal, regional, rol) y datos de liquidación/facturación (banco, CBU/alias, modalidad de cobro factura/liquidación, información de facturación). Los formularios SHALL validarse con React Hook Form + Zod, exigiendo los campos requeridos según la modalidad de cobro seleccionada.

#### Scenario: Crear usuario en relación de dependencia
- **WHEN** el ADMIN crea un usuario con modalidad de cobro "liquidación" y datos bancarios válidos
- **THEN** la feature envía el alta, muestra confirmación e invalida la query de usuarios

#### Scenario: Crear usuario facturante
- **WHEN** el ADMIN crea un usuario con modalidad "factura"
- **THEN** la feature persiste la modalidad de facturación y el usuario queda marcado como facturante

#### Scenario: Validación de campos requeridos
- **WHEN** el ADMIN intenta guardar sin un campo requerido
- **THEN** la feature bloquea el envío y muestra el error de validación

#### Scenario: Error de backend en alta
- **WHEN** el backend responde 422 por datos inválidos o identificación duplicada
- **THEN** la feature muestra el mensaje sin perder los datos del formulario

### Requirement: Activación y desactivación de usuario
La feature SHALL permitir al ADMIN activar o desactivar un usuario, invalidando la query del listado tras el cambio.

#### Scenario: Desactivar usuario activo
- **WHEN** el ADMIN desactiva un usuario activo
- **THEN** la feature envía el cambio de estado y el listado muestra el usuario como inactivo

### Requirement: Acceso restringido a administración de usuarios
La feature SHALL ocultar la entrada de menú y las acciones de ABM a usuarios sin permiso de gestión de usuarios, y SHALL manejar un 403 del backend mostrando acceso denegado.

#### Scenario: Sin permiso de gestión de usuarios
- **WHEN** el usuario no tiene permiso de gestión de usuarios ni `*:*`
- **THEN** la feature no muestra el item de menú ni las acciones de ABM

#### Scenario: Backend rechaza por permiso
- **WHEN** el backend responde 403 a una operación sobre usuarios
- **THEN** la feature muestra un mensaje de acceso denegado y no modifica el estado local
