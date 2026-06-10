## Context

C-10 creó los modelos `Calificacion` (con `aprobado` derivado y almacenado) y `UmbralMateria` (umbral configurable por asignación). El guard `atrasados:ver` ya existe en la matriz de permisos (C-04). Este change no necesita nuevos modelos ni migraciones — toda la lógica opera sobre entidades existentes.

El proyecto ya cuenta con `openpyxl` para generación de archivos .xlsx (usado en C-09 para import). Se reutilizará para la exportación de TPs sin corregir (F2.6).

El patrón establecido en C-10 es: **repositorios hacen agregaciones/consultas, services aplican lógica de negocio**. Este change sigue ese patrón estrictamente.

## Goals / Non-Goals

**Goals:**
- Cómputo de alumnos atrasados (RN-06): detecta alumnos con actividades faltantes o nota < umbral.
- Ranking de actividades aprobadas (RN-09): ranking descendente, solo alumnos con ≥1 aprobada.
- Reportes rápidos por materia (F2.4): métricas clave consolidadas.
- Notas finales agrupadas (F2.5): promedio por alumno de actividades seleccionadas.
- Exportar TPs sin corregir a .xlsx (F2.6, RN-07/08): entregas textuales sin calificación.
- Monitor general (F2.7): vista transversal con filtros materia/regional/comisión/alumno/estado.
- Monitor de seguimiento (F2.8) y su extensión con rango de fechas (F2.9).
- Endpoints `/api/analisis/*` con guard `atrasados:ver`.
- Lógica de cálculo en Services, sin raw SQL en Services.

**Non-Goals:**
- No se modifican modelos existentes ni se crean nuevos.
- No se implementa comunicación con alumnos (C-12).
- No se sincroniza con Moodle WS para reportes de finalización.
- No se implementan dashboards ni gráficos (son responsabilidad del frontend).

## Decisions

### D1: Cómputo de atrasados en Service con datos del repositorio
- **Decisión**: `AnalisisService.atrasados()` obtiene todas las calificaciones de una materia vía `CalificacionRepository.get_by_materia()`, obtiene el padrón activo y las entradas, y computa en Python qué alumnos están atrasados según RN-06.
- **Alternativa considerada**: Hacer toda la lógica en SQL dentro del repositorio.
- **Razón**: RN-06 tiene dos condiciones (faltantes y nota < umbral) que requieren lógica condicional. La regla de negocio vive en el Service — el repositorio solo trae datos. Dado que las materias típicamente tienen cientos de alumnos (no miles), el volumen es manejable en memoria.

### D2: Ranking con agregación en Service
- **Decisión**: `AnalisisService.ranking()` obtiene calificaciones por materia, agrupa por alumno en Python, cuenta `aprobado=true`, filtra los que tienen ≥1 y ordena descendente.
- **Razón**: RN-09 exige excluir alumnos sin aprobadas. El filtrado es lógica de negocio pura (Service). La agregación en Python es simple y evita SQL complejo.

### D3: Notas finales como promedio simple de numéricas
- **Decisión**: La nota final agrupada es el promedio de `nota_numerica` de las actividades seleccionadas. Las actividades textuales se excluyen del promedio pero se listan como referencia.
- **Alternativa considerada**: Solo mostrar actividades numéricas y ocultar textuales.
- **Razón**: El profesor necesita la nota final cuantitativa, pero también saber qué actividades textuales están aprobadas o no. Excluir textuales del promedio evita mezclar escalas, pero listarlas da contexto completo.

### D4: Export xlsx con openpyxl y StreamingResponse
- **Decisión**: El endpoint `GET /api/analisis/exportar-tps` acepta `materia_id` y genera un archivo .xlsx en memoria usando `openpyxl`, servido como `StreamingResponse` con content-type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.
- **Alternativa considerada**: CSR en el frontend.
- **Razón**: openpyxl ya es dependencia del proyecto. Generar del lado del servidor asegura formato consistente y permite manejar volúmenes grandes sin bloquear el frontend. El patrón StreamingResponse ya se usa en otros módulos del sistema.

### D5: Monitores con filtros en repositorio paginados
- **Decisión**: Cada tipo de monitor (general F2.7, seguimiento F2.8/F2.9) es un método en `AnalisisService` que acepta filtros opcionales y los delega al repositorio. El repositorio construye la query con filtros dinámicos y paginación.
- **Razón**: Los filtros son múltiples y opcionales. Un repositorio con `get_all()` y filtros kwargs (heredado de `BaseRepository`) no escala para joins complejos (calificacion + entrada_padron + usuario). Se necesita un método específico en el repositorio con filtros explícitos.

### D6: Un solo archivo de servicio y un solo archivo de router
- **Decisión**: Toda la lógica de análisis vive en `services/analisis_service.py` con la clase `AnalisisService`. Todos los endpoints bajo `routers/analisis.py`.
- **Razón**: Las funcionalidades comparten datos (calificaciones, umbral, padrón). Separar en múltiples servicios llevaría a duplicación de consultas y lógica. Un servicio cohesivo es más mantenible que varios acoplados.

### D7: Métodos de agregación en CalificacionRepository
- **Decisión**: Se añaden métodos a `CalificacionRepository`: `get_by_materia_con_entrada()` (join con EntradaPadron para obtener datos del alumno), y `get_filtrado()` (para monitores con filtros dinámicos paginados).
- **Razón**: El repositorio es el lugar para consultas con joins y filtros SQL. El Service no contiene raw SQL — llama a estos métodos.

## Risks / Trade-offs

- **[Riesgo] Rendimiento en materias con muchos alumnos**: si una materia tiene +5000 alumnos, el cómputo en memoria de atrasados puede ser lento. → **Mitigación**: el service itera una sola vez sobre los datos (O(n)). Para casos extremos, se puede cachear el resultado con TTL en una futura iteración.
- **[Riesgo] Umbral no configurado para una asignación**: si el profesor no configuró umbral, se usa 60% por defecto. → **Mitigación**: `UmbralRepository.get_umbral_efectivo()` ya maneja este caso.
- **[Trade-off] Cómputo en memoria vs SQL**: procesar en Python es más lento que SQL puro. → **Mitigación**: el volumen de datos típico (cientos, no miles de registros) hace que la diferencia sea imperceptible. La claridad del código y la separación de concerns lo justifica.
- **[Riesgo] Export sin datos**: si no hay entregas sin calificar, el archivo .xlsx estaría vacío. → **Mitigación**: el endpoint retorna 200 con `{"total": 0, "mensaje": "No se encontraron entregas sin corregir"}` en lugar de generar un archivo vacío.
