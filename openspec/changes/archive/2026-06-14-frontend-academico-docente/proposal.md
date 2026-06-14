## Why

El shell de navegación (C-21) ya está operativo. Ahora es necesario implementar las pantallas del perfil PROFESOR que permitan gestionar la experiencia académica: importar calificaciones desde LMS, configurar umbrales de aprobación, visualizar alumnos atrasados con ranking, consultar reportes rápidos y notas finales, enviar comunicaciones a alumnos atrasados, y monitorear el seguimiento de actividades.

## What Changes

- **Nuevas rutas protegidas** bajo `/app/` para cada feature del perfil académico-docente
- **Sidebar extendido** con entradas de navegación para las nuevas secciones, visibles según permisos del usuario
- **Feature: Importación de calificaciones** — Flujo completo de 2 pasos: (1) subir archivo LMS → preview con actividades detectadas, (2) seleccionar actividades y confirmar importación
- **Feature: Umbral de aprobación** — Configuración del porcentaje mínimo y valores textuales aprobatorios por asignación, con feedback visual del recálculo
- **Feature: Alumnos atrasados** — Vista con ranking por materia, filtros, indicadores de gravedad, acceso directo a comunicar
- **Feature: Notas finales y reportes** — Dashboard con métricas consolidadas de la materia, selector de actividades para cálculo de nota final promedio por alumno
- **Feature: Comunicación a atrasados** — Flujo: preview con variables sustituidas → envío masivo → tracking de estado por lote
- **Feature: Monitores de seguimiento** — Tabla paginada con filtros (materia, comisión, regional, estado, búsqueda), vista de tutor/profesor con scope por asignación

## Capabilities

### New Capabilities
- `calificaciones-importar`: Importación de calificaciones desde archivo LMS con preview de actividades detectadas, selección de actividades a importar, confirmación con feedback visual de resultados (insertadas/actualizadas/advertencias)
- `gestion-umbral`: Configuración del umbral de aprobación (numérico y textual) por asignación del docente, con indicación visual del valor actual y confirmación del recálculo asociado
- `alumnos-atrasados`: Vista de alumnos atrasados ordenada por gravedad/cantidad de actividades, filtrable por materia, con acciones rápidas para comunicarse con atrasados
- `notas-finales-reportes`: Dashboard de métricas rápidas de la materia (total alumnos, actividades, aprobación) y cálculo de nota final promedio seleccionando actividades, con tabla de resultados por alumno
- `comunicacion-atrasados`: Redacción de comunicación con preview de variables sustituidas, envío masivo a grupo de destinatarios, y tracking del estado del lote (pendiente, enviado, errores)
- `monitor-seguimiento`: Vista paginada del estado de actividades por alumno con filtros (materia, comisión, regional, estado, búsqueda por nombre), con alcance según rol (profesor ve sus materias, coordinador ve todo el tenant)

### Modified Capabilities
*(Ninguna — todos los specs existentes son backend y no modifican requerimientos de frontend shell existente)*

## Impact

- **Frontend**: 6 nuevas carpetas feature bajo `frontend/src/features/` + actualización de `Router.tsx`, `Layout.tsx`, y `App.tsx`
- **Rutas nuevas**: `/calificaciones/importar`, `/calificaciones/umbral`, `/alumnos/atrasados`, `/reportes`, `/comunicaciones`, `/monitores`
- **Sidebar**: Nuevas entradas de navegación agrupadas bajo sección "Académico"
- **API**: Consume endpoints de los specs `gestion-calificaciones`, `gestion-umbral`, `reportes-y-notas`, `preview-comunicacion`, `endpoints-comunicacion`, `monitores`
- **Sin cambios en backend**: Todos los endpoints ya están especificados. Este change es 100% frontend.
