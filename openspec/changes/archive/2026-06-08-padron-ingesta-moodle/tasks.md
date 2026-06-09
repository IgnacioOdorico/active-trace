## 1. Modelos

- [x] 1.1 Crear `models/version_padron.py` — VersionPadron (materia_id, cohorte_id, cargado_por, activa)
- [x] 1.2 Crear `models/entrada_padron.py` — EntradaPadron (version_id, usuario_id nullable, nombre, apellidos, email cifrado, comision, regional)
- [x] 1.3 Crear migración Alembic 007: version_padron, entrada_padron

## 2. Cliente Moodle WS

- [x] 2.1 Crear `integrations/moodle_ws.py` — clase MoodleClient con sync de usuarios/actividades
- [x] 2.2 Implementar reintentos (máx 3, backoff exponencial) y mapeo de errores a 502
- [x] 2.3 Implementar sync nocturna programada (método independiente para el worker)

## 3. Procesamiento de archivos

- [x] 3.1 Implementar parser de .xlsx/.csv para padrón (con skill `xlsx` si está disponible)
- [x] 3.2 Implementar vista previa: detecta columnas y muestra N filas sin persistir
- [x] 3.3 Implementar confirmación: crea versión + entradas con email cifrado

## 4. Repositorio y Service

- [x] 4.1 Crear `repositories/padron_repository.py` — VersionPadronRepository, EntradaPadronRepository
- [x] 4.2 Crear `services/padron_service.py` — importar (con preview/confirmar), activar versión, vaciar materia

## 5. Schemas

- [x] 5.1 Crear `schemas/padron.py` — ImportPreviewResponse, VersionPadronResponse, EntradaPadronResponse

## 6. Router

- [x] 6.1 Crear `routers/padron.py` con endpoints bajo /api/padron/* (guard `padron:importar`)
- [x] 6.2 Implementar POST /api/padron/importar (con ?preview=true y ?confirmar=true)
- [x] 6.3 Implementar DELETE /api/padron/materia/{id}/vaciar
- [x] 6.4 Registrar router en `app/main.py`

## 7. Tests

- [x] 7.1 Tests de modelos: versionado (activar desactiva anterior), unicidad, PII cifrada
- [x] 7.2 Tests de endpoints: import con preview, confirmar, vaciar, 403, 422
- [x] 7.3 Tests de Moodle WS: mock de respuestas, fallback a import manual, error 502
- [x] 7.4 Test de audit: import genera PADRON_CARGAR con filas_afectadas

## 8. Verificación

- [x] 8.1 `pytest` — todos los tests pasan
- [x] 8.2 `ruff check .` — sin errores
