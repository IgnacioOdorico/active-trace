## ADDED Requirements

### Requirement: El sistema SHALL modelar Calificacion con nota numérica y/o textual
`Calificacion` representa la nota de un estudiante en una actividad evaluable. Cada calificación pertenece a una entrada de padrón y una materia. Los campos `nota_numerica` y `nota_textual` no son mutuamente excluyentes.

#### Scenario: Crear calificación numérica
- **WHEN** se importa una calificación con nota_numerica=85.5
- **THEN** el sistema crea la Calificacion con nota_numerica=85.5 y nota_textual=null

#### Scenario: Crear calificación textual
- **WHEN** se importa una calificación con nota_textual="Satisfactorio"
- **THEN** el sistema crea la Calificacion con nota_textual="Satisfactorio" y nota_numerica=null

#### Scenario: Crear calificación con ambos valores
- **WHEN** se importa una calificación con nota_numerica=70 y nota_textual="Aprobado"
- **THEN** el sistema almacena ambos valores

### Requirement: El sistema SHALL derivar y almacenar `aprobado` según las reglas de negocio
El campo `aprobado` se calcula al importar y se recalcula al cambiar el umbral de la materia.

#### Scenario: Calificación numérica supera umbral
- **WHEN** una calificación tiene nota_numerica=75 y el umbral de la materia es 60%
- **THEN** aprobado=true

#### Scenario: Calificación numérica no supera umbral
- **WHEN** una calificación tiene nota_numerica=40 y el umbral de la materia es 60%
- **THEN** aprobado=false

#### Scenario: Calificación textual aprobatoria
- **WHEN** una calificación tiene nota_textual="Supera lo esperado"
- **THEN** aprobado=true

#### Scenario: Calificación textual no aprobatoria
- **WHEN** una calificación tiene nota_textual="No satisfactorio"
- **THEN** aprobado=false

### Requirement: El sistema SHALL importar calificaciones desde archivo LMS (F1.1)
El endpoint `POST /api/calificaciones/preview` acepta un archivo .xlsx/.csv y retorna las actividades detectadas. Luego `POST /api/calificaciones/importar` persiste las calificaciones de las actividades seleccionadas.

#### Scenario: Preview detecta columnas numéricas y textuales
- **WHEN** se sube un archivo .xlsx con columnas "TP1 (Real)", "TP2 (Real)", "Participación"
- **THEN** el sistema detecta "TP1 (Real)" y "TP2 (Real)" como numéricas, "Participación" como textual si contiene valores de la escala configurada

#### Scenario: Preview retorna actividades detectadas
- **WHEN** se sube un archivo .xlsx válido a POST /api/calificaciones/preview
- **THEN** el sistema retorna 200 con la lista de actividades detectadas y sus tipos (numerica/textual)

#### Scenario: Importar seleccionando actividades
- **WHEN** se envía POST /api/calificaciones/importar con materia_id y lista de actividades seleccionadas
- **THEN** el sistema persiste las Calificaciones para los alumnos del padrón activo de esa materia
- **AND** calcula aprobado según el umbral configurado

#### Scenario: Importar sin permiso retorna 403
- **WHEN** se envía POST /api/calificaciones/importar sin permiso `calificaciones:importar`
- **THEN** el sistema retorna 403

#### Scenario: Importar archivo con formato inválido retorna 422
- **WHEN** se sube un archivo que no es .xlsx ni .csv
- **THEN** el sistema retorna 422

### Requirement: El sistema SHALL ser idempotente al re-importar el mismo archivo (UPSERT)
Si ya existe una Calificacion para la misma combinación `(entrada_padron_id, nombre_actividad)`, se reemplazan los valores. No se lanza error.

#### Scenario: Re-importar actualiza calificaciones existentes
- **WHEN** se importa un archivo con calificaciones para "TP1" del alumno A
- **AND** luego se re-importa el mismo archivo con notas corregidas para "TP1" del mismo alumno
- **THEN** la Calificacion existente se actualiza con los nuevos valores
- **AND** la respuesta incluye `{insertadas: N, actualizadas: M}`

#### Scenario: Unique constraint (entrada_padron_id, nombre_actividad)
- **WHEN** se importan calificaciones
- **THEN** la combinación `(entrada_padron_id, nombre_actividad)` es única en la tabla calificacion
- **AND** el UPSERT usa esa constraint como clave de match

### Requirement: El sistema SHALL identificar alumnos por heurística de columnas del LMS
El parser detecta la columna de identificación del alumno entre las columnas del archivo. No exige un template fijo.

#### Scenario: Detecta columna Email
- **WHEN** el archivo tiene una columna llamada "Email" o "Dirección de correo"
- **THEN** el sistema usa esa columna para matchear contra entradas del padrón por email

#### Scenario: Detecta columna Nombre + Apellido(s)
- **WHEN** el archivo NO tiene columna Email pero tiene "Nombre" y "Apellido(s)"
- **THEN** el sistema intenta matchear por nombre completo contra el padrón

#### Scenario: Sin columna de identificación retorna error
- **WHEN** el archivo no tiene Email, Nombre ni Apellido(s)
- **THEN** el sistema retorna 422 con mensaje "No se pudo identificar la columna de alumnos"

### Requirement: El sistema SHALL manejar errores por fila sin abortar todo el import
Filas con datos faltantes o malformados se skipean o registran como advertencia. El import no se aborta.

#### Scenario: Fila sin identificación de alumno se skipea
- **WHEN** el archivo contiene una fila sin Email ni Nombre (fila vacía o subtotal)
- **THEN** el sistema skipea esa fila
- **AND** la respuesta incluye la fila como advertencia

#### Scenario: Valor numérico malformado en columna numérica se registra como null
- **WHEN** una fila tiene un valor no numérico (ej. "N/A", "-") en una columna con sufijo "(Real)"
- **THEN** el sistema registra nota_numerica=null para esa calificación
- **AND** aprobado=false
- **AND** la respuesta incluye la fila como advertencia

#### Scenario: Archivo vacío retorna 422
- **WHEN** el archivo .xlsx o .csv no tiene filas de datos (solo encabezados o vacío)
- **THEN** el sistema retorna 422 con mensaje "El archivo no contiene datos de alumnos"

#### Scenario: Archivo sin actividades detectadas retorna 422
- **WHEN** el archivo tiene columnas de identificación pero ninguna columna adicional que sea actividad evaluable
- **THEN** el sistema retorna 422 con mensaje "No se detectaron actividades evaluables en el archivo"

### Requirement: El sistema SHALL importar reporte de finalización (F1.2)
El endpoint `POST /api/calificaciones/reporte-finalizacion` acepta un archivo del LMS y retorna las entregas textuales sin calificación registrada.

#### Scenario: Reporte detecta entregas sin calificar
- **WHEN** se sube un archivo de finalización donde un alumno tiene "Entregado" en una actividad textual sin calificación
- **THEN** el sistema incluye esa entrega en la tabla de "posibles trabajos sin corregir"

#### Scenario: Reporte ignora actividades numéricas sin nota
- **WHEN** un alumno no tiene nota_numerica en una actividad numérica
- **THEN** no se incluye como "posible trabajo sin corregir"

### Requirement: La importación de calificaciones SHALL generar audit CALIFICACIONES_IMPORTAR
Cada importación confirmada genera un registro de auditoría.

#### Scenario: Importación genera audit
- **WHEN** se confirma una importación de calificaciones
- **THEN** el sistema registra audit con accion="CALIFICACIONES_IMPORTAR" y filas_afectadas igual a la cantidad de calificaciones importadas
