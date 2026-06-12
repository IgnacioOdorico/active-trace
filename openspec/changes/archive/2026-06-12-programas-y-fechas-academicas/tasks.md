## 1. Modelos y migración

- [x] 1.1 Crear `backend/app/models/programa_materia.py` con `ProgramaMateria(Base, EntityMeta)`: id, tenant_id, materia_id (UUID FK), carrera_id (UUID FK), cohorte_id (UUID FK), titulo (String(200)), referencia_archivo (String(500)), cargado_at (DateTime).
- [x] 1.2 Crear `backend/app/models/fecha_academica.py` con `FechaAcademica(Base, EntityMeta)`: id, tenant_id, materia_id (UUID FK), cohorte_id (UUID FK), tipo (String(20)), numero (Integer), periodo (String(20)), fecha (Date), titulo (String(200)). Incluir enum Python `TipoFechaAcademica`.
- [x] 1.3 Registrar ambos modelos en `backend/app/models/__init__.py`.
- [x] 1.4 Crear migración Alembic con tablas `programa_materia` y `fecha_academica`.

## 2. Repositorios

- [x] 2.1 Crear `backend/app/repositories/programa_materia_repository.py` con `ProgramaMateriaRepository(BaseRepository[ProgramaMateria])`: método `get_by_materia_carrera_cohorte(materia_id, carrera_id, cohorte_id, db)`.
- [x] 2.2 Crear `backend/app/repositories/fecha_academica_repository.py` con `FechaAcademicaRepository(BaseRepository[FechaAcademica])`: método `get_by_materia_cohorte(materia_id, cohorte_id, db)`.
- [x] 2.3 Registrar ambos repositorios en `backend/app/repositories/__init__.py`.

## 3. Schemas

- [x] 3.1 Crear `backend/app/schemas/programa.py` con modelos Pydantic: `ProgramaMateriaResponse`, `ProgramaMateriaCreateRequest`, `ProgramaMateriaUpdateRequest`, `ProgramaMateriaListResponse`.
- [x] 3.2 Crear `backend/app/schemas/fecha_academica.py` con modelos Pydantic: `FechaAcademicaResponse`, `FechaAcademicaCreateRequest`, `FechaAcademicaUpdateRequest`, `FechaAcademicaListResponse`, `FragmentoLMSResponse`.

## 4. Services

- [x] 4.1 Crear `backend/app/services/programa_service.py` con `ProgramaService`: inyecta `ProgramaMateriaRepository`. Métodos: `crear`, `editar`, `eliminar`, `listar`, `obtener`.
- [x] 4.2 Crear `backend/app/services/fecha_academica_service.py` con `FechaAcademicaService`: inyecta `FechaAcademicaRepository`. Métodos: `crear`, `editar`, `eliminar`, `listar`, `generar_fragmento_lms`.

## 5. Routers

- [x] 5.1 Crear `backend/app/routers/programas.py` con `APIRouter(prefix="/api/programas")`.
- [x] 5.2 Endpoint `POST /` — guard `estructura:gestionar` → `ProgramaService.crear()`.
- [x] 5.3 Endpoint `GET /` — guard `estructura:gestionar` → `ProgramaService.listar()`.
- [x] 5.4 Endpoint `GET /{id}` — guard `estructura:gestionar` → `ProgramaService.obtener()`.
- [x] 5.5 Endpoint `PATCH /{id}` — guard `estructura:gestionar` → `ProgramaService.editar()`.
- [x] 5.6 Endpoint `DELETE /{id}` — guard `estructura:gestionar` → `ProgramaService.eliminar()`.
- [x] 5.7 Crear `backend/app/routers/fechas_academicas.py` con `APIRouter(prefix="/api/fechas-academicas")`.
- [x] 5.8 Endpoint `POST /` — guard `estructura:gestionar` → `FechaAcademicaService.crear()`.
- [x] 5.9 Endpoint `GET /` — guard `estructura:gestionar` → `FechaAcademicaService.listar()`.
- [x] 5.10 Endpoint `GET /{id}` — guard `estructura:gestionar` → detalle.
- [x] 5.11 Endpoint `PATCH /{id}` — guard `estructura:gestionar` → `FechaAcademicaService.editar()`.
- [x] 5.12 Endpoint `DELETE /{id}` — guard `estructura:gestionar` → `FechaAcademicaService.eliminar()`.
- [x] 5.13 Endpoint `GET /lms/{materia_id}/{cohorte_id}` — guard `estructura:gestionar` → `FechaAcademicaService.generar_fragmento_lms()`.
- [x] 5.14 Registrar ambos routers en `app/main.py`.

## 6. Tests

- [x] 6.1 Tests de programas: CRUD, filtros por materia/carrera/cohorte, 403 sin permiso.
- [x] 6.2 Tests de fechas académicas: CRUD, filtros, fragmento LMS, 403 sin permiso.
- [x] 6.3 Tests de aislamiento tenant.

## 7. Verificación

- [x] 7.1 `pytest` — todos los tests pasan.
- [x] 7.2 `ruff check .` — sin errores en código nuevo.
