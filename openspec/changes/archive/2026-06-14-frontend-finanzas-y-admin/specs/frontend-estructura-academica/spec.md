## ADDED Requirements

### Requirement: ABM de carreras
La feature SHALL permitir a usuarios con permiso `estructura:gestionar` listar, crear, editar y cambiar el estado (activa/inactiva) de carreras del tenant, mediante hooks de TanStack Query sobre `apiClient` (`GET/POST/PATCH` sobre el módulo de estructura, ej. `/api/v1/estructura/carreras`). Los formularios SHALL validarse con React Hook Form + Zod (código y nombre requeridos).

#### Scenario: Crear carrera
- **WHEN** el usuario completa código y nombre y confirma
- **THEN** la feature envía el alta, muestra confirmación e invalida la query de carreras

#### Scenario: Cambiar estado de carrera
- **WHEN** el usuario desactiva una carrera activa
- **THEN** la feature envía el cambio de estado y el listado refleja la carrera como inactiva

#### Scenario: Validación de campos requeridos
- **WHEN** el usuario intenta guardar sin código o sin nombre
- **THEN** la feature bloquea el envío y muestra el error de validación

### Requirement: ABM de cohortes
La feature SHALL permitir listar, crear, editar y cambiar el estado de cohortes (nombre, año de inicio, fechas de vigencia desde/hasta, estado) con permiso `estructura:gestionar`. La validación SHALL exigir que `desde` sea anterior a `hasta`.

#### Scenario: Crear cohorte
- **WHEN** el usuario completa nombre, año y fechas de vigencia válidas y confirma
- **THEN** la feature envía el alta y la cohorte aparece en el listado

#### Scenario: Vigencia inválida
- **WHEN** el usuario ingresa una fecha `desde` posterior a `hasta`
- **THEN** la feature bloquea el envío y muestra el error de validación

### Requirement: ABM de materias
La feature SHALL permitir listar, crear y editar materias del tenant con permiso `estructura:gestionar`, reutilizando el hook de catálogo de materias existente (`useMaterias` de `features/academico`) para lecturas compartidas.

#### Scenario: Crear materia
- **WHEN** el usuario completa los datos de la materia y confirma
- **THEN** la feature envía el alta e invalida la query de materias

#### Scenario: Listado vacío
- **WHEN** el endpoint de materias responde vacío
- **THEN** la feature muestra un estado informativo sin romper la tabla

### Requirement: Registro de ruta y menú de Administración
La feature SHALL registrar su página en `frontend/src/pages/Router.tsx` y agregar el item de menú en la sección "Administración" de `Layout.tsx` con `requiredPermission: 'estructura:gestionar'`.

#### Scenario: Menú visible según permiso
- **WHEN** el usuario tiene permiso `estructura:gestionar`
- **THEN** el item de menú de Estructura Académica aparece en la sección Administración

#### Scenario: Menú oculto sin permiso
- **WHEN** el usuario no tiene `estructura:gestionar` ni `*:*`
- **THEN** el item de menú no se muestra
