## ADDED Requirements

### Requirement: ABM de Salario Base por rol con vigencia
La feature SHALL permitir a usuarios con permiso `liquidaciones:configurar-salarios` listar, crear y actualizar registros de SalarioBase (rol, monto, desde, hasta) mediante hooks de TanStack Query sobre `apiClient` (`GET/POST/PATCH /api/v1/salario-base`). El formulario SHALL validarse con React Hook Form + Zod, exigiendo monto positivo y, cuando `hasta` no sea nula, que `desde` sea anterior a `hasta`.

#### Scenario: Crear salario base válido
- **WHEN** el usuario completa rol=PROFESOR, monto válido y fecha desde, y confirma
- **THEN** la feature envía `POST /api/v1/salario-base`, muestra confirmación e invalida la query de salario base para refrescar el listado

#### Scenario: Rechazo de solapamiento temporal del backend
- **WHEN** el backend responde 422 por solapamiento de vigencia para el mismo rol
- **THEN** la feature muestra el mensaje de error sin perder los datos cargados en el formulario

#### Scenario: Cerrar vigencia abierta
- **WHEN** el usuario edita un SalarioBase con `hasta=null` seteando una fecha hasta
- **THEN** la feature envía `PATCH /api/v1/salario-base/{id}` y el registro deja de figurar como vigente

#### Scenario: Validación de forma en cliente
- **WHEN** el usuario ingresa una fecha `desde` posterior a `hasta`
- **THEN** la feature bloquea el envío y muestra el error de validación sin llamar al backend

### Requirement: ABM de Salario Plus por grupo y rol con vigencia
La feature SHALL permitir listar, crear y actualizar registros de SalarioPlus (grupo, rol, monto, descripción, desde, hasta) mediante `GET/POST/PATCH /api/v1/salario-plus`, con la misma validación de vigencia y permiso `liquidaciones:configurar-salarios`.

#### Scenario: Crear plus salarial para un grupo y rol
- **WHEN** el usuario completa grupo="PROG", rol=PROFESOR, monto y desde, y confirma
- **THEN** la feature envía `POST /api/v1/salario-plus` y el plus aparece en el listado

#### Scenario: Plus con vigencia acotada
- **WHEN** el usuario crea un plus con desde y hasta definidos
- **THEN** la feature persiste ambas fechas y el listado refleja la vigencia acotada

### Requirement: Acceso restringido por permiso
La feature SHALL ocultar las acciones de creación/edición y la entrada de menú a usuarios sin `liquidaciones:configurar-salarios`, y SHALL manejar un 403 del backend mostrando acceso denegado sin romper la vista.

#### Scenario: Sin permiso de configuración salarial
- **WHEN** el usuario no tiene `liquidaciones:configurar-salarios` ni `*:*`
- **THEN** la feature no muestra el item de menú ni las acciones de ABM

#### Scenario: Backend rechaza por permiso
- **WHEN** el backend responde 403 a una operación de grilla salarial
- **THEN** la feature muestra un mensaje de acceso denegado y no modifica el estado local
