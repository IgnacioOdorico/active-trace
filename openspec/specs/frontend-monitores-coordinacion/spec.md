## ADDED Requirements

### Requirement: Monitor general del tenant (coordinación)
La feature SHALL mostrar al usuario con permiso de coordinación el monitor general transversal (F2.7) con el estado de actividades de todos los alumnos del tenant, desde el endpoint de análisis correspondiente, con filtros por materia, regional, comisión, búsqueda libre por alumno, estado de actividad y criterio de clasificación. SHALL reutilizar el hook y los componentes del feature `monitor-seguimiento` existente sin duplicar la lógica de fetch.

#### Scenario: Filtros del monitor general
- **WHEN** el coordinador aplica filtros de materia y estado de actividad
- **THEN** la feature llama el endpoint con esos query params y renderiza solo los alumnos coincidentes

#### Scenario: Limpiar selección
- **WHEN** el usuario pulsa "Limpiar"
- **THEN** los filtros se resetean y el listado vuelve al estado sin filtrar

### Requirement: Monitor de seguimiento coordinación/admin con rango de fechas
La feature SHALL ofrecer el monitor de seguimiento (F2.9) que extiende la vista de tutor/profesor agregando filtro por rango de fechas (`fecha_desde`/`fecha_hasta`) para acotar el período de análisis.

#### Scenario: Filtro por rango de fechas
- **WHEN** el coordinador define un rango de fechas
- **THEN** la feature envía `fecha_desde` y `fecha_hasta` y el monitor refleja solo ese período

### Requirement: Acceso restringido por permiso
La entrada de menú y la ruta del monitor de coordinación SHALL ser visibles solo para sesiones con el permiso correspondiente (`monitores:ver` / `atrasados:ver`), aplicando el filtro de permisos del shell.

#### Scenario: Usuario sin permiso
- **WHEN** un usuario sin el permiso de coordinación abre el menú
- **THEN** el ítem del monitor de coordinación no aparece
