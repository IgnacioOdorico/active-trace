## 1. Modelos y migración

- [x] 1.1 Crear `backend/app/models/slot_encuentro.py` con `SlotEncuentro(Base, EntityMeta)`: id, tenant_id, asignacion_id, materia_id, titulo (String(200)), hora (Time), dia_semana (String(15)), fecha_inicio (Date), cant_semanas (Integer, default 0), fecha_unica (Date nullable), meet_url (String(500)), vig_desde (Date), vig_hasta (Date nullable). Incluir enum Python `DiaSemana` con Lunes–Domingo.
- [x] 1.2 Crear `backend/app/models/instancia_encuentro.py` con `InstanciaEncuentro(Base, EntityMeta)`: id, tenant_id, slot_id (UUID nullable FK), materia_id, fecha (Date), hora (Time), titulo (String(200)), estado (String(20), default "Programado"), meet_url (String(500)), video_url (String(500) nullable), comentario (Text nullable). Incluir enum Python `EstadoEncuentro`.
- [x] 1.3 Crear `backend/app/models/guardia.py` con `Guardia(Base, EntityMeta)`: id, tenant_id, asignacion_id, materia_id, carrera_id, cohorte_id (UUID nullable), dia (String(15)), horario (String(20)), estado (String(20), default "Pendiente"), comentarios (Text nullable). Incluir enum Python `EstadoGuardia`.
- [x] 1.4 Registrar los 3 modelos en `backend/app/models/__init__.py`.
- [x] 1.5 Crear migración Alembic con tablas `slot_encuentro`, `instancia_encuentro`, `guardia`.

## 2. Repositorios

- [x] 2.1 Crear `backend/app/repositories/slot_encuentro_repository.py` con `SlotEncuentroRepository(BaseRepository[SlotEncuentro])`.
- [x] 2.2 Crear `backend/app/repositories/instancia_encuentro_repository.py` con `InstanciaEncuentroRepository(BaseRepository[InstanciaEncuentro])`: método `get_by_slot(slot_id, session)`, `get_by_materia_filtros(materia_id, fecha_desde, fecha_hasta, estado, session)` para admin list.
- [x] 2.3 Crear `backend/app/repositories/guardia_repository.py` con `GuardiaRepository(BaseRepository[Guardia])`: método `get_by_asignacion(asignacion_id, session)`, método `get_all_filtros(materia_id, asignacion_id, session)`.
- [x] 2.4 Registrar los 3 repositorios en `backend/app/repositories/__init__.py`.

## 3. Schemas

- [x] 3.1 Crear `backend/app/schemas/encuentro.py` con modelos Pydantic: `SlotEncuentroResponse`, `InstanciaEncuentroResponse`, `InstanciaEncuentroListResponse`, `CrearSlotRecurrenteRequest`, `CrearEncuentroUnicoRequest`, `EditarInstanciaRequest`, `GenerarHTMLResponse`.
- [x] 3.2 Crear `backend/app/schemas/guardia.py` con modelos Pydantic: `GuardiaResponse`, `GuardiaListResponse`, `CrearGuardiaRequest`, `EditarGuardiaRequest`, `ExportGuardiasResponse`.

## 4. Service — EncuentroService

- [x] 4.1 Crear `backend/app/services/encuentro_service.py` con `EncuentroService`: inyecta `SlotEncuentroRepository`, `InstanciaEncuentroRepository`, `AuditLogService`.
- [x] 4.2 Implementar `_calcular_fechas(fecha_inicio, dia_semana, cant_semanas)`: valida que fecha_inicio coincida con dia_semana, calcula N fechas semanales.
- [x] 4.3 Implementar `crear_slot_recurrente(data, usuario_id, db)`: crea slot, genera instancias con `_calcular_fechas`, persiste todo en transacción. Registra audit log `ENCUENTRO_CREAR`.
- [x] 4.4 Implementar `crear_encuentro_unico(data, db)`: crea InstanciaEncuentro sin slot_id. Registra audit log `ENCUENTRO_CREAR`.
- [x] 4.5 Implementar `editar_instancia(instancia_id, data, db)`: modifica estado, meet_url, video_url, comentario. Valida transiciones de estado (Programado→Realizado, Programado→Cancelado; rechaza otras). Registra audit log `ENCUENTRO_EDITAR`.
- [x] 4.6 Implementar `generar_html(materia_id, db)`: obtiene instancias de la materia, genera tabla HTML con `string.Template`.
- [x] 4.7 Implementar `listar(filtros, pagina, page_size, db)`: listado paginado para admin con filtros por materia_id, fecha_desde, fecha_hasta, estado.
- [x] 5.1 Crear `backend/app/services/guardia_service.py` con `GuardiaService`: inyecta `GuardiaRepository`, `AuditLogService`.
- [x] 5.2 Implementar `crear(data, usuario_id, db)`: crea guardia con asignacion_id del usuario autenticado. Registra audit log `GUARDIA_CREAR`.
- [x] 5.3 Implementar `listar_mis_guardias(asignacion_id, pagina, page_size, db)`: lista guardias por asignación del tutor.
- [x] 5.4 Implementar `listar_todas(filtros, pagina, page_size, db)`: listado global para coordinación con filtros.
- [x] 5.5 Implementar `editar(guardia_id, data, db)`: modifica estado y comentarios. Valida transiciones.
- [x] 5.6 Implementar `exportar(filtros, db)`: retorna lista JSON de guardias con datos desnormalizados.

## 6. Routers

- [x] 6.1 Crear `backend/app/routers/encuentros.py` con `APIRouter(prefix="/api/encuentros")`.
- [x] 6.2 Endpoint `POST /slots` — guard `encuentros:gestionar` → `EncuentroService.crear_slot_recurrente()`.
- [x] 6.3 Endpoint `POST /instancias` — guard `encuentros:gestionar` → `EncuentroService.crear_encuentro_unico()`.
- [x] 6.4 Endpoint `PATCH /instancias/{id}` — guard `encuentros:gestionar` → `EncuentroService.editar_instancia()`.
- [x] 6.5 Endpoint `GET /html/{materia_id}` — guard `encuentros:gestionar` → `EncuentroService.generar_html()`.
- [x] 6.6 Endpoint `GET /instancias` — guard `encuentros:gestionar` → `EncuentroService.listar()`.
- [x] 6.7 Crear `backend/app/routers/guardias.py` con `APIRouter(prefix="/api/guardias")`.
- [x] 6.8 Endpoint `POST /` — guard `encuentros:gestionar` → `GuardiaService.crear()`.
- [x] 6.9 Endpoint `GET /` — guard `encuentros:gestionar` → `GuardiaService.listar_mis_guardias()` o `listar_todas()` según rol.
- [x] 6.10 Endpoint `PATCH /{id}` — guard `encuentros:gestionar` → `GuardiaService.editar()`.
- [x] 6.11 Endpoint `GET /exportar` — guard `encuentros:gestionar` → `GuardiaService.exportar()`.
- [x] 6.12 Registrar ambos routers en `app/main.py`.

## 7. Permisos

- [x] 7.1 Crear permiso `encuentros:gestionar` en el seed/catálogo de permisos.

## 8. Audit

- [x] 8.1 Agregar constantes `ENCUENTRO_CREAR`, `ENCUENTRO_EDITAR`, `GUARDIA_CREAR` en `AuditLogService`.

## 9. Tests

- [x] 9.1 Tests de generación de instancias recurrentes: slot con cant_semanas=8 genera 8 instancias, validación fecha_inicio vs dia_semana, límite cant_semanas ≤ 52.
- [x] 9.2 Tests de encuentro único: creación sin slot_id, datos mínimos, rechazo sin materia_id.
- [x] 9.3 Tests de edición de instancia: Programado→Realizado, Programado→Cancelado, agregar video_url, transición inválida Cancelado→Realizado, 404 en ID inexistente.
- [x] 9.4 Tests de generación HTML: materia con encuentros retorna tabla, materia sin encuentros retorna párrafo, meet_url como link, video_url como link.
- [x] 9.5 Tests de admin list: paginación, filtros por materia/fecha/estado, límite page_size ≤ 100.
- [x] 9.6 Tests de guardias: crear guardia, listar mis guardias, listar todas (coordinación), editar estado, transición inválida, 404 en guardia de otro tutor.
- [x] 9.7 Tests de exportación: exportar guardias sin filtros, exportar filtrada por materia.
- [x] 9.8 Tests de auditoría: verificar audit log en creación de slot, encuentro único, edición de instancia, creación de guardia.

## 10. Verificación

- [x] 10.1 `pytest` — todos los tests pasan.
- [x] 10.2 `ruff check .` — sin errores en código nuevo.
