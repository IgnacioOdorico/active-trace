## ADDED Requirements

### Requirement: El sistema SHALL generar reportes rápidos por materia (F2.4)
El endpoint `GET /api/analisis/reportes/{materia_id}` retorna métricas consolidadas de la materia a partir de los datos importados.

#### Scenario: Reporte retorna métricas clave
- **WHEN** se consulta GET /api/analisis/reportes/{materia_id}
- **THEN** el sistema retorna 200 con: total_alumnos (en padrón activo), total_actividades (detectadas en import), total_calificaciones, promedio_aprobacion_general, alumnos_atrasados_count, alumnos_aprobados_count

#### Scenario: Reporte sin datos retorna métricas en cero
- **WHEN** se consulta reportes para una materia sin calificaciones importadas
- **THEN** el sistema retorna 200 con métricas en 0 y un indicador `sin_datos: true`

### Requirement: El sistema SHALL calcular notas finales agrupadas (F2.5)
El endpoint `POST /api/analisis/notas-finales` acepta materia_id y lista de actividades, y retorna la nota final promedio por alumno.

#### Scenario: Nota final promedio de actividades numéricas
- **WHEN** se envía POST /api/analisis/notas-finales con materia_id y actividades=["TP1", "TP2", "Parcial"]
- **THEN** el sistema retorna por cada alumno: nombre, apellidos, comisión, lista de notas por actividad, nota_final (promedio de numéricas), actividades_textuales (referencia)

#### Scenario: Actividades textuales se excluyen del promedio
- **WHEN** una actividad seleccionada es textual (solo nota_textual)
- **THEN** no se incluye en el cálculo de nota_final
- **AND** se lista en actividades_textuales para referencia del profesor

#### Scenario: Alumno sin notas numéricas tiene nota_final nula
- **WHEN** un alumno solo tiene actividades textuales seleccionadas
- **THEN** su nota_final es null y se indica "Sin nota numérica"

#### Scenario: Actividad no encontrada retorna 422
- **WHEN** se envía una actividad que no existe en las calificaciones de la materia
- **THEN** el sistema retorna 422 con mensaje "Actividad no encontrada: {nombre}"
