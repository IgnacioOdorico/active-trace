## ADDED Requirements

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

#### Scenario: Configurar valores textuales aprobatorios
- **WHEN** el usuario agrega "Satisfactorio" y "Excelente" como valores textuales aprobatorios
- **THEN** el frontend envía PUT /api/umbral/{asignacion_id} con valores_aprobatorios=["Satisfactorio", "Excelente"]
- **AND** muestra los valores guardados como tags removibles

#### Scenario: Validación de umbral fuera de rango
- **WHEN** el usuario ingresa un umbral_pct menor a 0 o mayor a 100
- **THEN** el frontend muestra error de validación "El porcentaje debe estar entre 0 y 100"
- **AND** no permite enviar el formulario
