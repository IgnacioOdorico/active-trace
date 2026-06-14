## 1. Infraestructura y routing

- [x] 1.1 Extender `Layout.tsx` con nuevas entradas de navegación agrupadas bajo sección "Académico" en el sidebar
- [x] 1.2 Agregar rutas protegidas en `Router.tsx` para las 6 nuevas features bajo el Layout existente
- [x] 1.3 Crear carpeta base `features/academico/` con barrel exports y tipos compartidos del dominio académico

## 2. Importación de calificaciones (`features/calificaciones-importar/`)

- [x] 2.1 Crear hook `useCalificacionesApi` con queries/mutations para preview e importación
- [x] 2.2 Implementar página Paso 1: selector de materia, upload de archivo, botón "Vista Previa"
- [x] 2.3 Implementar tabla de preview con actividades detectadas, checkboxes de selección y tipo (numérica/textual)
- [x] 2.4 Implementar página Paso 2: confirmación con resumen de insertadas/actualizadas/advertencias expandibles
- [x] 2.5 Manejar estados: loading (spinner en subida), error (formato inválido, sin actividades), empty state

## 3. Configuración de umbral (`features/gestion-umbral/`)

- [x] 3.1 Crear hook `useUmbralApi` con query para obtener umbral actual y mutation para actualizar
- [x] 3.2 Implementar formulario con selector de asignación/materia, campo numérico umbral_pct y tags de valores textuales
- [x] 3.3 Implementar visualización de umbral por defecto (60%) con indicador cuando no hay configuración
- [x] 3.4 Implementar validación Zod (rango 0-100) y feedback post-guardado con conteo de recálculo

## 4. Alumnos atrasados (`features/alumnos-atrasados/`)

- [x] 4.1 Crear hook `useAtrasadosApi` con query para listar atrasados con filtros
- [x] 4.2 Implementar tabla ranking con columnas: nombre, actividades_no_aprobadas, total, progreso, última_actividad
- [x] 4.3 Implementar indicadores visuales de gravedad (Crítico/Atención/Seguimiento) por umbral de porcentaje
- [x] 4.4 Implementar filtro por materia y paginación server-side
- [x] 4.5 Implementar botón "Comunicar" por fila que navega a `/comunicaciones` con contexto preseleccionado

## 5. Notas finales y reportes (`features/notas-finales-reportes/`)

- [x] 5.1 Crear hook `useReportesApi` con query para métricas y mutation para notas finales
- [x] 5.2 Implementar dashboard de tarjetas de métricas (total_alumnos, total_actividades, promedio_aprobacion, etc.)
- [x] 5.3 Implementar empty state con enlace a importación cuando `sin_datos: true`
- [x] 5.4 Implementar selector de actividades (numéricas) con badge "Textual" en actividades textuales
- [x] 5.5 Implementar tabla de resultados de nota final por alumno con botón de descarga CSV

## 6. Comunicación a atrasados (`features/comunicacion-atrasados/`)

- [x] 6.1 Crear hook `useComunicacionesApi` con queries/mutations para preview, envío, tracking y cancelación
- [x] 6.2 Implementar formulario de redacción: asunto_template, cuerpo_template, selector de materia, selector de destinatarios
- [x] 6.3 Implementar panel de preview inline con variables sustituidas y marcado "Solo lectura"
- [x] 6.4 Implementar envío masivo con confirmación y redirección a tracking del lote
- [x] 6.5 Implementar vista de tracking por lote: tabla con estados coloreados, filtros por estado
- [x] 6.6 Implementar botones de aprobación/rechazo de lote (solo visible con permiso `comunicacion:aprobar`)

## 7. Monitores de seguimiento (`features/monitor-seguimiento/`)

- [x] 7.1 Crear hook `useMonitoresApi` con queries para monitor-general y monitor-seguimiento
- [x] 7.2 Implementar monitor general: tabla paginada con filtros (materia, comisión, regional, búsqueda, estado)
- [x] 7.3 Implementar monitor seguimiento con scope según rol (profesor ve sus materias, coordinador ve todo)
- [x] 7.4 Implementar selector de alumno y filtro de actividad mínima en seguimiento
- [x] 7.5 Implementar rango de fechas condicional (visible solo para coordinadores)
