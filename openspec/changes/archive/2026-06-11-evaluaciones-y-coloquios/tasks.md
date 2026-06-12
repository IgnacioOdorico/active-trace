## 1. Modelos y migración

- [x] 1.1 Crear `backend/app/models/evaluacion.py` con `Evaluacion(Base, EntityMeta)`: id, tenant_id, materia_id, cohorte_id, tipo (String(20)), instancia (String(200)), dias_disponibles (Integer). Incluir enum Python `TipoEvaluacion` con Parcial, TP, Coloquio, Recuperatorio.
- [x] 1.2 Crear `backend/app/models/evaluacion_dia.py` con `EvaluacionDia(Base, EntityMeta)`: id, evaluacion_id (UUID FK), fecha (Date), cupo_maximo (Integer), cupos_restantes (Integer).
- [x] 1.3 Crear `backend/app/models/reserva_evaluacion.py` con `ReservaEvaluacion(Base, EntityMeta)`: id, tenant_id, evaluacion_dia_id (UUID FK), alumno_id (UUID FK), fecha_hora (DateTime), estado (String(20), default "Activa"). Incluir enum Python `EstadoReserva` con Activa, Cancelada.
- [x] 1.4 Crear `backend/app/models/resultado_evaluacion.py` con `ResultadoEvaluacion(Base, EntityMeta)`: id, tenant_id, evaluacion_id (UUID FK), alumno_id (UUID FK), nota_final (String(20)).
- [x] 1.5 Crear `backend/app/models/evaluacion_alumno.py` con `EvaluacionAlumno(Base, EntityMeta)`: id, evaluacion_id (UUID FK), alumno_id (UUID FK). Tabla pivote para padrón de alumnos habilitados.
- [x] 1.6 Registrar los 5 modelos en `backend/app/models/__init__.py`.
- [x] 1.7 Crear migración Alembic con tablas `evaluacion`, `evaluacion_dia`, `reserva_evaluacion`, `resultado_evaluacion`, `evaluacion_alumno`.

## 2. Repositorios

- [x] 2.1 Crear `backend/app/repositories/evaluacion_repository.py` con `EvaluacionRepository(BaseRepository[Evaluacion])`: método `get_with_metricas(evaluacion_id, session)`, método `list_all_con_metricas(filtros, pagina, page_size, session)` para admin list.
- [x] 2.2 Crear `backend/app/repositories/evaluacion_dia_repository.py` con `EvaluacionDiaRepository(BaseRepository[EvaluacionDia])`: método `decrementar_cupo(dia_id, session)` — UPDATE condicional `SET cupos_restantes = cupos_restantes - 1 WHERE id = :id AND cupos_restantes > 0`, método `incrementar_cupo(dia_id, session)`, método `get_by_evaluacion(evaluacion_id, session)`.
- [x] 2.3 Crear `backend/app/repositories/reserva_evaluacion_repository.py` con `ReservaEvaluacionRepository(BaseRepository[ReservaEvaluacion])`: método `get_activas_por_alumno(alumno_id, session)`, método `get_activas_por_evaluacion(evaluacion_id, session)`, método `contar_activas(evaluacion_id, session)`.
- [x] 2.4 Crear `backend/app/repositories/resultado_evaluacion_repository.py` con `ResultadoEvaluacionRepository(BaseRepository[ResultadoEvaluacion])`: método `get_por_evaluacion(evaluacion_id, session)`, método `upsert(evaluacion_id, alumno_id, nota_final, session)`.
- [x] 2.5 Crear `backend/app/repositories/evaluacion_alumno_repository.py` con `EvaluacionAlumnoRepository(BaseRepository[EvaluacionAlumno])`: método `reemplazar_padron(evaluacion_id, alumno_ids, session)` — DELETE + INSERT en transacción, método `get_alumnos_habilitados(evaluacion_id, session)`.
- [x] 2.6 Registrar los 5 repositorios en `backend/app/repositories/__init__.py`.

## 3. Schemas

- [x] 3.1 Crear `backend/app/schemas/coloquio.py` con modelos Pydantic: `EvaluacionResponse`, `EvaluacionDiaResponse`, `ReservaEvaluacionResponse`, `ResultadoEvaluacionResponse`, `CrearEvaluacionRequest`, `ImportarAlumnosRequest`, `ReservarTurnoRequest`, `RegistrarResultadoRequest`, `MetricasResponse`, `MetricasConvocatoriaResponse`, `AgendaResponse`, `ConvocatoriaDisponibleResponse`.

## 4. Service — ColoquioService

- [x] 4.1 Crear `backend/app/services/coloquio_service.py` con `ColoquioService`: inyecta `EvaluacionRepository`, `EvaluacionDiaRepository`, `ReservaEvaluacionRepository`, `ResultadoEvaluacionRepository`, `EvaluacionAlumnoRepository`, `AuditLogService`.
- [x] 4.2 Implementar `crear_convocatoria(data, usuario_id, db)`: crea Evaluacion, genera N registros EvaluacionDia con cupo_maximo y cupos_restantes. Registra audit log `COLOQUIO_CREAR`.
- [x] 4.3 Implementar `importar_alumnos(evaluacion_id, alumno_ids, db)`: reemplaza padrón atómicamente (DELETE + INSERT en transacción). Valida que todos los alumno_id existan en Usuario.
- [x] 4.4 Implementar `reservar_turno(evaluacion_id, evaluacion_dia_id, usuario_id, db)`: verifica rol ALUMNO, padrón habilitado, cupo disponible. Decrementa cupo con UPDATE condicional. Crea ReservaEvaluacion. Registra audit log `COLOQUIO_RESERVAR`.
- [x] 4.5 Implementar `cancelar_reserva(reserva_id, usuario_id, db)`: verifica que la reserva pertenezca al usuario, cambia estado a Cancelada, incrementa cupo_restantes del día. Registra audit log `COLOQUIO_RESERVAR` con detalle "cancelada".
- [x] 4.6 Implementar `listar_mis_reservas(usuario_id, db)`: retorna reservas activas del alumno con datos de evaluación y día.
- [x] 4.7 Implementar `registrar_resultado(evaluacion_id, alumno_id, nota_final, db)`: crea o actualiza ResultadoEvaluacion. Valida que el alumno esté en el padrón.
- [x] 4.8 Implementar `listar_resultados(evaluacion_id, db)`: retorna resultados con datos del alumno.
- [x] 4.9 Implementar `obtener_metricas_globales(tenant_id, db)`: total alumnos convocados, instancias activas, reservas activas, notas registradas.
- [x] 4.10 Implementar `obtener_metricas_convocatoria(evaluacion_id, db)`: convocados, reservas activas, cupos libres, notas registradas.
- [x] 4.11 Implementar `listar_convocatorias(filtros, pagina, page_size, db)`: listado paginado con métricas embebidas para admin list (F7.4).
- [x] 4.12 Implementar `obtener_agenda(evaluacion_id, db)`: reservas activas ordenadas por fecha con datos del alumno (F7.5).
- [x] 4.13 Implementar `cerrar_convocatoria(evaluacion_id, db)`: marca evaluación como cerrada. Registra audit log `COLOQUIO_CERRAR`.
- [x] 4.14 Implementar `editar_convocatoria(evaluacion_id, data, db)`: modifica campos editables. Rechaza si está cerrada.
- [x] 4.15 Implementar `listar_disponibles(usuario_id, db)`: convocatorias activas donde el alumno está habilitado y hay cupo.

## 5. Routers

- [x] 5.1 Crear `backend/app/routers/coloquios.py` con `APIRouter(prefix="/api/coloquios")`.
- [x] 5.2 Endpoint `POST /` — guard `coloquios:gestionar` → `ColoquioService.crear_convocatoria()`.
- [x] 5.3 Endpoint `GET /` — guard `coloquios:gestionar` → `ColoquioService.listar_convocatorias()`.
- [x] 5.4 Endpoint `GET /disponibles` — guard `coloquios:reservar` → `ColoquioService.listar_disponibles()`. (Definir antes de `GET /{id}` por orden de rutas.)
- [x] 5.5 Endpoint `GET /{id}` — guard `coloquios:gestionar` → detalle de evaluación.
- [x] 5.6 Endpoint `PATCH /{id}` — guard `coloquios:gestionar` → `ColoquioService.editar_convocatoria()`.
- [x] 5.7 Endpoint `PATCH /{id}/cerrar` — guard `coloquios:gestionar` → `ColoquioService.cerrar_convocatoria()`.
- [x] 5.8 Endpoint `POST /{id}/alumnos` — guard `coloquios:gestionar` → `ColoquioService.importar_alumnos()`.
- [x] 5.9 Endpoint `POST /{id}/reservar` — guard `coloquios:reservar` → `ColoquioService.reservar_turno()`.
- [x] 5.10 Endpoint `GET /mis-reservas` — guard `coloquios:reservar` → `ColoquioService.listar_mis_reservas()`. (Definir antes de `GET /{id}` por orden de rutas.)
- [x] 5.11 Endpoint `PATCH /reservas/{id}/cancelar` — guard `coloquios:reservar` → `ColoquioService.cancelar_reserva()`.
- [x] 5.12 Endpoint `POST /{id}/resultados` — guard `coloquios:gestionar` → `ColoquioService.registrar_resultado()`.
- [x] 5.13 Endpoint `GET /{id}/resultados` — guard `coloquios:gestionar` → `ColoquioService.listar_resultados()`.
- [x] 5.14 Endpoint `GET /metricas` — guard `coloquios:gestionar` → `ColoquioService.obtener_metricas_globales()`. (Definir antes de `GET /{id}` por orden de rutas.)
- [x] 5.15 Endpoint `GET /{id}/metricas` — guard `coloquios:gestionar` → `ColoquioService.obtener_metricas_convocatoria()`.
- [x] 5.16 Endpoint `GET /{id}/agenda` — guard `coloquios:gestionar` → `ColoquioService.obtener_agenda()`.
- [x] 5.17 Registrar router `coloquios` en `app/main.py`.

## 6. Permisos

- [x] 6.1 Crear permiso `coloquios:gestionar` en el seed/catálogo de permisos.
- [x] 6.2 Crear permiso `coloquios:reservar` en el seed/catálogo de permisos.
- [x] 6.3 Asignar `coloquios:gestionar` a roles COORDINADOR y ADMIN.
- [x] 6.4 Asignar `coloquios:reservar` a rol ALUMNO.

## 7. Audit

- [x] 7.1 Agregar constantes `COLOQUIO_CREAR`, `COLOQUIO_RESERVAR`, `COLOQUIO_CERRAR` en `AuditLogService`.

## 8. Tests

- [x] 8.1 Tests de creación de convocatoria con cupos: creación exitosa, genera N días con cupo, rechazo sin materia/cohorte, rechazo tipo inválido, 403 sin permiso.
- [x] 8.2 Tests de importación de alumnos: importar alumnos, reemplaza padrón anterior, alumno inexistente retorna 404, 403 sin permiso.
- [x] 8.3 Tests de reserva de turno: reserva exitosa decrementa cupo, cupo agotado rechaza (409), alumno no habilitado rechaza (403), 403 sin permiso coloquios:reservar.
- [x] 8.4 Tests de cancelación de reserva: cancelación exitosa incrementa cupo, cancelar reserva de otro alumno retorna 403, cancelar reserva ya cancelada retorna 400.
- [x] 8.5 Tests de listado de reservas del alumno: lista reservas activas, alumno sin reservas retorna vacío.
- [x] 8.6 Tests de registro de resultados: registrar nota, actualizar nota existente, 403 sin permiso.
- [x] 8.7 Tests de consulta de resultados: lista resultados por evaluación, evaluación sin resultados retorna vacío, 403 sin permiso.
- [x] 8.8 Tests de métricas globales: métricas con datos, métricas sin datos retornan ceros, 403 sin permiso.
- [x] 8.9 Tests de métricas por convocatoria: métricas de convocatoria con datos, convocatoria sin alumnos retorna métricas en cero.
- [x] 8.10 Tests de listado de convocatorias: listado paginado, filtro por materia, sin datos retorna vacío, 403 sin permiso.
- [x] 8.11 Tests de agenda de reservas: agenda ordenada por fecha, sin reservas retorna vacío, 403 sin permiso.
- [x] 8.12 Tests de cierre de convocatoria: cerrar exitosamente, cerrar ya cerrada retorna 400, 403 sin permiso.
- [x] 8.13 Tests de edición de convocatoria: editar exitosamente, editar cerrada retorna 400.
- [x] 8.14 Tests de convocatorias disponibles para alumno: lista disponibles donde está habilitado, excluye donde no tiene cupo.
- [x] 8.15 Tests de auditoría: verificar audit log en creación de convocatoria, reserva, cancelación, cierre.
- [x] 8.16 Tests de concurrencia: dos reservas simultáneas al último cupo, solo una debe ser exitosa.

## 9. Verificación

- [x] 9.1 `pytest` — todos los tests pasan (732 passed, 1 pre-existing failure `test_asignacion_exactamente_en_desde`).
- [x] 9.2 `ruff check .` — sin errores en código nuevo.
