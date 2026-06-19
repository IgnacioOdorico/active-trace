## ADDED Requirements

### Requirement: El sistema SHALL modelar UmbralMateria por asignación docente
`UmbralMateria` define el criterio de aprobación para una asignación específica (docente × materia). Si no existe configuración, se usa el valor por defecto del sistema (60%).

#### Scenario: Crear umbral con valor personalizado
- **WHEN** un docente configura umbral_pct=75 para su asignación
- **THEN** el sistema crea UmbralMateria con umbral_pct=75 para esa asignacion_id

#### Scenario: Umbral por defecto sin configuración
- **WHEN** no existe UmbralMateria para una asignación
- **THEN** el sistema usa umbral_pct=60 como valor por defecto

### Requirement: El sistema SHALL permitir configurar el umbral de aprobación (F2.1, RN-03)
El endpoint `PUT /api/umbral/{asignacion_id}` permite al profesor definir el porcentaje mínimo aprobatorio y los valores textuales aprobatorios para su materia.

#### Scenario: Configurar umbral exitoso
- **WHEN** un profesor envía PUT /api/umbral/{asignacion_id} con umbral_pct=70
- **THEN** el sistema actualiza el umbral
- **AND** recalcula aprobado en todas las calificaciones de esa asignación

#### Scenario: Umbral de un docente no afecta a otros
- **WHEN** el profesor A cambia su umbral a 70%
- **THEN** las calificaciones del profesor B en la misma materia no se ven afectadas

### Requirement: El sistema SHALL permitir configurar valores textuales aprobatorios
El endpoint acepta una lista de valores textuales que cuentan como aprobado.

#### Scenario: Configurar valores textuales aprobatorios
- **WHEN** un profesor configura valores_aprobatorios=["Satisfactorio", "Supera lo esperado", "Excelente"]
- **THEN** el sistema usa esos valores para determinar aprobado en calificaciones textuales

#### Scenario: Valor textual no listado no es aprobatorio
- **WHEN** una calificación tiene nota_textual="Regular" y "Regular" no está en valores_aprobatorios
- **THEN** aprobado=false

### Requirement: La importación de calificaciones SHALL usar el umbral configurado
Al importar calificaciones, el sistema usa el UmbralMateria vigente para determinar aprobado.

#### Scenario: Import usa umbral configurado
- **WHEN** se importan calificaciones y existe UmbralMateria con umbral_pct=75
- **THEN** aprobado se calcula contra ese umbral

### Requirement: El sistema SHALL mostrar formulario de configuración de umbral
El frontend SHALL proveer un formulario donde el profesor selecciona su asignación (materia) y configura el umbral de aprobación.

#### Scenario: Formulario muestra umbral actual precargado
- **WHEN** el usuario navega a `/calificaciones/umbral` y selecciona una materia
- **THEN** el frontend consulta GET /api/umbral/{asignacion_id} (o un endpoint que retorne el umbral actual)
- **AND** precarga el formulario con el valor actual de umbral_pct y valores_aprobatorios textuales
- **AND** si no hay configuración previa, muestra el valor por defecto (60%) con indicación "Valor por defecto del sistema"

#### Scenario: Actualizar umbral numérico
- **WHEN** el usuario cambia umbral_pct a 75 y hace clic en "Guardar"
- **THEN** el frontend envía PUT /api/umbral/{asignacion_id} con umbral_pct=75
- **AND** muestra confirmación "Umbral actualizado. Se recalcularon N calificaciones."
- **AND** muestra el nuevo valor como umbral activo

#### Scenario: Configurar valores textuales aprobatorios (frontend)
- **WHEN** el usuario agrega "Satisfactorio" y "Excelente" como valores textuales aprobatorios
- **THEN** el frontend envía PUT /api/umbral/{asignacion_id} con valores_aprobatorios=["Satisfactorio", "Excelente"]
- **AND** muestra los valores guardados como tags removibles

#### Scenario: Validación de umbral fuera de rango
- **WHEN** el usuario ingresa un umbral_pct menor a 0 o mayor a 100
- **THEN** el frontend muestra error de validación "El porcentaje debe estar entre 0 y 100"
- **AND** no permite enviar el formulario
