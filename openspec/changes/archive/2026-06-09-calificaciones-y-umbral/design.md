## Context

C-09 creó el padrón versionado (VersionPadron/EntradaPadron). C-10 construye sobre eso: las calificaciones referencian `entrada_padron_id` y se importan desde archivos del LMS. Cada calificación se evalúa contra un umbral configurable por asignación docente (UmbralMateria).

No existen aún modelos, repositorios ni servicios de calificaciones o umbral. El proyecto ya tiene el skill `xlsx` para procesamiento de archivos (usado en C-09).

`Calificacion.nota_numerica` y `Calificacion.nota_textual` son mutuamente no exclusivos (una calificación puede tener ambos). El campo `aprobado` es derivado pero se almacena para performance de consultas; se recalcula al cambiar el umbral.

## Goals / Non-Goals

**Goals:**
- Modelos `Calificacion` (con `aprobado` almacenado y derivado) y `UmbralMateria`.
- Import desde archivo .xlsx/.csv del LMS con detección de columnas numéricas (RN-01) y textuales (RN-02), vista previa, selección de actividades.
- Import de reporte de finalización (F1.2): detecta TPs textuales entregados sin calificación.
- Configurar umbral por asignación (F2.1, RN-03, defecto 60%). Recalcula `aprobado` de las calificaciones afectadas.
- Audit `CALIFICACIONES_IMPORTAR`.
- `Migración 0NN: calificacion, umbral_materia`.

**Non-Goals:**
- No se implementa la detección de atrasados (C-11).
- No se implementa ranking de actividades (C-11).
- No se implementa comunicación con alumnos (C-12).
- No se sincroniza con Moodle WS para calificaciones (la sincro es manual vía archivo).

## Decisions

### D1: `aprobado` almacenado con recalculo al cambiar umbral
- **Decisión**: `Calificacion.aprobado` es un campo booleano almacenado. Se calcula al importar y se recalcula vía UPDATE batch cuando cambia el umbral de la asignación.
- **Alternativa considerada**: Calcular `aprobado` on-the-fly en cada consulta.
- **Razón**: C-11 (ranking y atrasados) requiere consultas frecuentes sobre `aprobado`. Recalcular en cada query escala mal. Como el umbral cambia raramente (una vez por período), el costo de recalcular batch es despreciable.

### D2: UmbralMateria referencias Asignacion, no Usuario
- **Decisión**: La FK de `UmbralMateria` apunta a `Asignacion`, no directamente a `Usuario`.
- **Razón**: RN-03 exige que el umbral de un docente no afecte a otros. `Asignacion` ya modela la relación (docente × materia × cohorte × rol). Esto garantiza aislamiento sin lógica adicional.

### D3: Import con preview-confirm como C-09
- **Decisión**: El flujo de importación replica el patrón de C-09: `POST /api/calificaciones/preview` para detectar columnas y mostrar actividades, luego `POST /api/calificaciones/importar` con las actividades seleccionadas.
- **Razón**: Consistencia con la experiencia de importación de padrón. El usuario revisa antes de persistir.

### D4: Reporte de finalización es un import separado
- **Decisión**: F1.2 tiene su propio endpoint `POST /api/calificaciones/reporte-finalizacion`. El resultado es una tabla de TPs textuales sin calificación (no persiste calificaciones nuevas).
- **Razón**: Son dos archivos distintos del LMS. Mezclarlos en un solo flujo complica la UX y el modelo de datos.

### D5: Detección de columnas por heurística de encabezados
- **Decisión**: Columnas con encabezado terminado en `(Real)` son numéricas (RN-01). Las demás columnas con valores textuales conocidos ("Satisfactorio", "Supera lo esperado", etc.) se detectan como textuales. Columnas sin contenido evaluable se ignoran.
- **Razón**: El LMS exporta con convenciones de nomenclatura fijas. No necesitamos configuración adicional por tenant en esta etapa.

### D6: Import idempotente — UPSERT por (entrada_padron_id, nombre_actividad)
- **Decisión**: Si ya existe una `Calificacion` para el mismo `(entrada_padron_id, nombre_actividad)`, se **reemplazan** los valores (nota_numerica, nota_textual, aprobado, origen). No se lanza error, no se saltea. El modelo tiene unique constraint `(entrada_padron_id, nombre_actividad)`.
- **Alternativa considerada**: Lanzar error ("ya existen calificaciones para esta actividad") o ignorar filas duplicadas.
- **Razón**: El profesor puede re-subir el mismo archivo después de corregir notas en el LMS. Re-subir es un caso de uso REAL del día a día. Si falla o ignora, el usuario se frustra. UPSERT es el comportamiento esperado: "subí de nuevo y se actualizó".
- **Impacto en audit**: `CALIFICACIONES_IMPORTAR` reporta `filas_afectadas` = total procesado (inserts + updates). El detalle del JSON incluye `{insertadas: N, actualizadas: M}`.

### D7: Columnas de identificación del alumno y formato esperado del archivo LMS
- **Decisión**: El parser busca la columna de identificación del alumno en orden de prioridad: "Email" / "Dirección de correo" → "Nombre" + "Apellido(s)" → "DNI". Debe encontrar AL MENOS UNA columna de identificación para procesar el archivo. Las demás columnas se tratan como actividades evaluables.
- **Razón**: Moodle permite configurar qué datos exporta. En lugar de exigir un schema fijo, detectamos por heurística de encabezado. Esto cubre variantes de configuración del LMS sin depender de un template exacto.

### D8: Manejo de errores por fila — fail-fast con reporte detallado
- **Decisión**: Si una fila NO tiene identificación de alumno (no se pudo determinar a qué entrada_padron pertenece), se **skip** con reporte en la respuesta. Si una fila tiene un valor numérico malformado en una columna numérica (ej. "N/A" en columna "(Real)"), se registra como `nota_numerica=null` y `aprobado=false`, y se incluye en la respuesta como advertencia. NO se aborta todo el import por una fila mala.
- **Alternativa considerada**: Abortar todo el import si alguna fila tiene error.
- **Razón**: El archivo del LMS puede tener filas de totales, subtotales, o alumnos dados de baja. Abortar por unas pocas filas malas obliga al usuario a editar el archivo manualmente. Skip + reporte es más robusto.
- **Impacto en audit**: El JSON de audit incluye `{errores: [...], advertencias: [...]}`.

## Risks / Trade-offs

- **[Riesgo] Archivo LMS con formato inesperado**: si el LMS cambia su formato de exportación, la detección de columnas falla. → **Mitigación**: error claro ("Formato de archivo no reconocido") con detalle de columnas esperadas vs. encontradas.
- **[Riesgo] Recalculo de `aprobado` en umbral concurrente**: si dos docentes cambian umbral simultáneamente. → **Mitigación**: el recalculo opera por `asignacion_id`; no hay condición de carrera porque cada docente es dueño de su umbral.
- **[Trade-off] Almacenar `aprobado` duplica lógica**: el valor derivado debe mantenerse sincronizado. → **Mitigación**: el recalculo es transaccional (UPDATE dentro de la misma transacción que cambia el umbral).
