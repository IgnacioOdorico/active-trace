## ADDED Requirements

### Requirement: Visualizar avisos según perfil del usuario
El sistema SHALL exponer un endpoint GET /api/avisos que retorna solo los avisos que corresponden al perfil del usuario autenticado, aplicando los siguientes filtros:
1. Avisos activos (`activo = true`) y sin soft delete
2. Dentro de la ventana de vigencia (`inicio_en <= ahora <= fin_en`)
3. Que coincidan con el perfil del usuario según alcance:
   - Global: todos los ven
   - PorMateria: usuarios con asignación en esa materia
   - PorCohorte: usuarios con asignación en esa cohorte
   - PorRol: usuarios con el rol especificado
4. Si `rol_destino` está definido, el usuario debe tener ese rol
5. Ordenados por `orden` ascendente (más prioritario primero)

#### Scenario: Usuario ve avisos globales
- **WHEN** un ALUMNO autenticado consulta GET /api/avisos
- **THEN** el sistema retorna los avisos globales activos dentro de vigencia
- **THEN** no retorna avisos fuera de vigencia

#### Scenario: Usuario ve avisos por materia
- **WHEN** un PROFESOR autenticado consulta avisos y está asignado a materias
- **THEN** el sistema retorna avisos globales + avisos de las materias donde está asignado

#### Scenario: Usuario no ve avisos de otra cohorte
- **WHEN** un usuario consulta avisos
- **THEN** el sistema NO incluye avisos con alcance PorCohorte dirigidos a cohortes donde el usuario no está asignado

#### Scenario: Aviso fuera de vigencia no se muestra
- **WHEN** un usuario consulta avisos y hay un aviso con fin_en anterior a la fecha actual
- **THEN** el sistema no incluye ese aviso en la respuesta

#### Scenario: Orden de prioridad
- **WHEN** un usuario consulta avisos
- **THEN** los avisos se ordenan por orden ascendente (menor valor = mayor prioridad)

#### Scenario: Aviso inactivo no se muestra
- **WHEN** un usuario consulta avisos y hay un aviso con activo=false
- **THEN** el sistema no incluye ese aviso en la respuesta
