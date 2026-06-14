## 1. Modelos

- [x] 1.1 Crear `models/calificacion.py` — Calificacion con unique constraint `(entrada_padron_id, nombre_actividad)`, campos (entrada_padron_id, materia_id, actividad, nota_numerica, nota_textual, aprobado, origen Importado|Manual, importado_at)
- [x] 1.2 Crear `models/umbral_materia.py` — UmbralMateria (asignacion_id, materia_id, umbral_pct, valores_aprobatorios como JSON)
- [x] 1.3 Crear migración Alembic 008: calificacion, umbral_materia

## 2. Repositorios

- [x] 2.1 Crear `repositories/calificacion_repository.py` — bulk upsert (ON CONFLICT DO UPDATE), recalcular aprobado por asignacion_id
- [x] 2.2 Crear `repositories/umbral_repository.py` — upsert por asignacion_id, get con defecto 60%

## 3. Procesamiento de archivos

- [x] 3.1 Implementar parser de .xlsx/.csv para calificaciones: detecta columnas numéricas (RN-01: sufijo "(Real)") y textuales (RN-02)
- [x] 3.2 Implementar heurística de identificación de alumnos: detecta columna Email/Dirección de correo → Nombre+Apellido(s) → DNI
- [x] 3.3 Implementar validación por fila: filas sin identificación se skipean, valores numéricos malformados → null+no_aprobado
- [x] 3.4 Implementar preview: parsea archivo, detecta actividades, retorna muestra sin persistir
- [x] 3.5 Implementar validaciones de archivo: vacío → 422, sin actividades detectadas → 422
- [x] 3.6 Implementar parser de reporte de finalización (F1.2): detecta TPs textuales entregados sin nota

## 4. Services

- [x] 4.1 Crear `services/calificacion_service.py` — preview, importar (UPSERT idempotente con reporte insertadas/actualizadas), reporte-finalizacion, recalcular-aprobado, manejo de errores por fila
- [x] 4.2 Crear `services/umbral_service.py` — configurar umbral (con recalculo batch de aprobado), obtener umbral vigente

## 5. Schemas

- [x] 5.1 Crear `schemas/calificacion.py` — ImportPreviewResponse, CalificacionResponse, ImportRequest, ImportResponse
- [x] 5.2 Crear `schemas/umbral.py` — UmbralConfigRequest, UmbralMateriaResponse

## 6. Router

- [x] 6.1 Crear `routers/calificaciones.py` con endpoints bajo /api/calificaciones/* (guard `calificaciones:importar`)
- [x] 6.2 Crear `routers/umbral.py` con endpoints bajo /api/umbral/*
- [x] 6.3 Registrar routers en `app/main.py`

## 7. Tests

- [x] 7.1 Tests de modelos: derivación aprobado (numérica vs umbral, textual vs conjunto aprobatorio)
- [x] 7.2 Tests de endpoints: import con preview, confirmar, 403 sin permiso, 422 formato inválido
- [x] 7.3 Tests de idempotencia: re-import actualiza existentes, reporta insertadas/actualizadas
- [x] 7.4 Tests de validación de schema: fila sin identificación skipea, valor malformado → null, archivo vacío 422, sin actividades 422
- [x] 7.5 Tests de umbral: configurar, recalcula aprobado, no afecta otros docentes (misma materia, distinta asignación)
- [x] 7.6 Test de audit: import genera CALIFICACIONES_IMPORTAR con filas_afectadas y detalle insertadas/actualizadas

## 8. Verificación

- [x] 8.1 `pytest` — todos los tests pasan
- [x] 8.2 `ruff check .` — sin errores en código nuevo
