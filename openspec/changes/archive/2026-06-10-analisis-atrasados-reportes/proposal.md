## Why

C-10 habilitó la importación de calificaciones y la configuración de umbrales. Sin el módulo de análisis, el profesor no puede identificar alumnos en riesgo, rankear aprobaciones ni generar reportes académicos. Este change completa el flujo central del PROFESOR (FL-02 pasos 5-6) añadiendo las capacidades de análisis, ranking, monitores y exportación que transforman los datos importados en información accionable.

## What Changes

- **Alumnos atrasados** (F2.2, RN-06): cómputo que cruza calificaciones contra umbral configurado para detectar alumnos con actividades faltantes o nota inferior al umbral.
- **Ranking de actividades aprobadas** (F2.3, RN-09): ranking descendente de alumnos por cantidad de actividades aprobadas, excluyendo alumnos sin ninguna aprobada.
- **Reportes rápidos por materia** (F2.4): métricas consolidadas de la materia a partir de datos importados.
- **Notas finales agrupadas** (F2.5): agrupación de actividades seleccionadas y cálculo de nota final por alumno.
- **Exportar TPs sin corregir** (F2.6, RN-07/08): archivo descargable con entregas textuales detectadas como pendientes de corrección.
- **Monitor general** (F2.7): vista transversal del tenant con filtros (materia, regional, comisión, alumno, estado).
- **Monitor de seguimiento** (F2.8, F2.9): vista filtrable para tutor/profesor, extendida con rango de fechas para coordinación/admin.
- **Nuevos endpoints** bajo `/api/analisis/*` con guard `atrasados:ver`. Sin nuevos modelos ni migraciones — toda la lógica opera sobre `Calificacion`, `UmbralMateria` y `EntradaPadron` existentes.

## Capabilities

### New Capabilities
- `analisis-core`: cómputo de alumnos atrasados (RN-06) y ranking de actividades aprobadas (RN-09), con lógica de cálculo en Services (sin SQL en Services).
- `reportes-y-notas`: reportes rápidos por materia (F2.4) y notas finales agrupadas (F2.5).
- `exportar-tps`: exportación de trabajos prácticos sin corregir a archivo descargable (F2.6, RN-07/08).
- `monitores`: monitor general (F2.7), monitor de seguimiento tutor/profesor (F2.8) y monitor coordinación/admin con rango de fechas (F2.9).

### Modified Capabilities
<!-- No existing capabilities change their requirements. -->

## Impact

- **Services**: se crea `services/analisis_service.py` con `AnalisisService` (atrasados, ranking, reportes, notas finales, export, monitores) — sin raw SQL, apoyado en repositorios existentes.
- **Repositories**: se añaden métodos de agregación/consulta a `CalificacionRepository` (atrasados, ranking, notas finales agrupadas, filtros de monitor) para que la lógica de negocio viva en Services.
- **Routers**: se crea `routers/analisis.py` con endpoints `/api/analisis/*` (guard `atrasados:ver`).
- **Schemas**: se crea `schemas/analisis.py` con modelos Pydantic para requests y responses de análisis.
- **No nuevos modelos DB ni migraciones** — todo opera sobre `Calificacion`, `UmbralMateria`, `EntradaPadron`, `VersionPadron`.
- **Dependencia**: openpyxl ya presente para exportación xlsx.
- **Tests**: definición de atrasado contra umbral, ranking (solo ≥1 aprobada), notas finales agrupadas, filtros del monitor, export.
