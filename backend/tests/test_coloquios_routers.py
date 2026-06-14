import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_current_user, get_db
from app.main import app
from app.models.user import User


class _MockSession:
    def __init__(self) -> None:
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        execute_result = Mock()
        execute_result.scalars.return_value.all.return_value = []
        execute_result.scalar_one_or_none.return_value = None
        execute_result.scalar_one.return_value = 0
        self.execute = AsyncMock(return_value=execute_result)
        self.flush = AsyncMock()
        self.refresh = AsyncMock()
        self.close = AsyncMock()
        self.add = Mock()
        self.get = AsyncMock()
        self.delete = Mock()


class TestColoquioRouters:
    _tenant_id = uuid.uuid4()
    _user_id = uuid.uuid4()

    @pytest.fixture(autouse=True)
    def mock_deps(self):
        async def _mock_user():
            user = Mock(spec=User)
            user.id = self._user_id
            user.tenant_id = self._tenant_id
            user.is_active = True
            user.impersonator_id = None
            return user

        async def _mock_db():
            return _MockSession()

        app.dependency_overrides[get_current_user] = _mock_user
        app.dependency_overrides[get_db] = _mock_db
        yield
        app.dependency_overrides.clear()

    # ---- 8.1: Creación de convocatoria con cupos ----

    @pytest.mark.asyncio
    async def test_crear_convocatoria_exitosa(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear_convocatoria = AsyncMock(return_value={
                "id": str(evaluacion_id),
                "materia_id": str(uuid.uuid4()),
                "cohorte_id": str(uuid.uuid4()),
                "tipo": "Coloquio",
                "instancia": "Coloquio Final",
                "dias_disponibles": 5,
                "dias_generados": 5,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/coloquios",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "tipo": "Coloquio",
                        "instancia": "Coloquio Final",
                        "dias_disponibles": 5,
                        "cupo_por_dia": 10,
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 201
                data = response.json()
                assert data["tipo"] == "Coloquio"
                assert data["dias_generados"] == 5

    @pytest.mark.asyncio
    async def test_crear_convocatoria_422_tipo_invalido(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/coloquios",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "tipo": "Examen",
                        "instancia": "Coloquio Final",
                        "dias_disponibles": 5,
                        "cupo_por_dia": 10,
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_crear_convocatoria_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/coloquios",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "tipo": "Coloquio",
                        "instancia": "Coloquio Final",
                        "dias_disponibles": 5,
                        "cupo_por_dia": 10,
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.2: Importación de alumnos ----

    @pytest.mark.asyncio
    async def test_importar_alumnos_exitoso(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.importar_alumnos = AsyncMock(return_value=3)

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/coloquios/{evaluacion_id}/alumnos",
                    json={
                        "alumno_ids": [str(uuid.uuid4()) for _ in range(3)],
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["cantidad_importados"] == 3

    @pytest.mark.asyncio
    async def test_importar_alumnos_403_sin_permiso(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/coloquios/{evaluacion_id}/alumnos",
                    json={"alumno_ids": [str(uuid.uuid4())]},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.3: Reserva de turno ----

    @pytest.mark.asyncio
    async def test_reservar_turno_exitoso(self):
        evaluacion_id = uuid.uuid4()
        dia_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.reservar_turno = AsyncMock(return_value={
                "id": str(uuid.uuid4()),
                "evaluacion_dia_id": str(dia_id),
                "fecha_hora": "2026-06-15T10:00:00+00:00",
                "estado": "Activa",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/coloquios/{evaluacion_id}/reservar",
                    json={"evaluacion_dia_id": str(dia_id)},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 201
                assert response.json()["estado"] == "Activa"

    @pytest.mark.asyncio
    async def test_reservar_turno_403_sin_permiso(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/coloquios/{evaluacion_id}/reservar",
                    json={"evaluacion_dia_id": str(uuid.uuid4())},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.4: Cancelación de reserva ----

    @pytest.mark.asyncio
    async def test_cancelar_reserva_exitosa(self):
        reserva_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.cancelar_reserva = AsyncMock(return_value={
                "id": str(reserva_id),
                "estado": "Cancelada",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/coloquios/reservas/{reserva_id}/cancelar",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["estado"] == "Cancelada"

    @pytest.mark.asyncio
    async def test_cancelar_reserva_ya_cancelada(self):
        reserva_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.cancelar_reserva = AsyncMock(side_effect=Mock(spec=Exception))
            from app.core.exceptions import DomainError
            mock_svc.cancelar_reserva = AsyncMock(
                side_effect=DomainError("La reserva ya está cancelada")
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/coloquios/reservas/{reserva_id}/cancelar",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 400

    # ---- 8.5: Listado de reservas del alumno ----

    @pytest.mark.asyncio
    async def test_listar_mis_reservas_activas(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_mis_reservas = AsyncMock(return_value=[
                {
                    "id": str(uuid.uuid4()),
                    "evaluacion_dia_id": str(uuid.uuid4()),
                    "alumno_id": str(self._user_id),
                    "fecha_hora": "2026-06-15T10:00:00+00:00",
                    "estado": "Activa",
                    "evaluacion_materia": "Coloquio",
                    "evaluacion_instancia": "Coloquio Final",
                    "dia_fecha": "2026-06-15",
                }
            ])

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/coloquios/mis-reservas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["estado"] == "Activa"

    @pytest.mark.asyncio
    async def test_listar_mis_reservas_vacio(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_mis_reservas = AsyncMock(return_value=[])

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/coloquios/mis-reservas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json() == []

    # ---- 8.6: Registro de resultados ----

    @pytest.mark.asyncio
    async def test_registrar_resultado_crea(self):
        evaluacion_id = uuid.uuid4()
        alumno_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.registrar_resultado = AsyncMock(return_value={
                "id": str(uuid.uuid4()),
                "evaluacion_id": str(evaluacion_id),
                "alumno_id": str(alumno_id),
                "nota_final": "8",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/coloquios/{evaluacion_id}/resultados",
                    json={"alumno_id": str(alumno_id), "nota_final": "8"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["nota_final"] == "8"

    @pytest.mark.asyncio
    async def test_registrar_resultado_403_sin_permiso(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/coloquios/{evaluacion_id}/resultados",
                    json={"alumno_id": str(uuid.uuid4()), "nota_final": "8"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.7: Consulta de resultados ----

    @pytest.mark.asyncio
    async def test_listar_resultados_exitoso(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_resultados = AsyncMock(return_value=[
                {
                    "id": str(uuid.uuid4()),
                    "evaluacion_id": str(evaluacion_id),
                    "alumno_id": str(uuid.uuid4()),
                    "nota_final": "8",
                    "alumno_nombre": "Juan",
                    "alumno_apellido": "Pérez",
                }
            ])

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/coloquios/{evaluacion_id}/resultados",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_listar_resultados_vacio(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_resultados = AsyncMock(return_value=[])

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/coloquios/{evaluacion_id}/resultados",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json() == []

    @pytest.mark.asyncio
    async def test_listar_resultados_403_sin_permiso(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/coloquios/{evaluacion_id}/resultados",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.8: Métricas globales ----

    @pytest.mark.asyncio
    async def test_metricas_globales_con_datos(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener_metricas_globales = AsyncMock(return_value={
                "total_alumnos_convocados": 20,
                "total_instancias_activas": 3,
                "total_reservas_activas": 15,
                "total_notas_registradas": 10,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/coloquios/metricas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["total_alumnos_convocados"] == 20
                assert data["total_instancias_activas"] == 3

    @pytest.mark.asyncio
    async def test_metricas_globales_sin_datos(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener_metricas_globales = AsyncMock(return_value={
                "total_alumnos_convocados": 0,
                "total_instancias_activas": 0,
                "total_reservas_activas": 0,
                "total_notas_registradas": 0,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/coloquios/metricas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["total_alumnos_convocados"] == 0

    @pytest.mark.asyncio
    async def test_metricas_globales_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/coloquios/metricas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.9: Métricas por convocatoria ----

    @pytest.mark.asyncio
    async def test_metricas_convocatoria_con_datos(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener_metricas_convocatoria = AsyncMock(return_value={
                "convocados": 15,
                "reservas_activas": 8,
                "cupos_libres": 22,
                "notas_registradas": 5,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/coloquios/{evaluacion_id}/metricas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["convocados"] == 15

    @pytest.mark.asyncio
    async def test_metricas_convocatoria_sin_alumnos(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener_metricas_convocatoria = AsyncMock(return_value={
                "convocados": 0,
                "reservas_activas": 0,
                "cupos_libres": 50,
                "notas_registradas": 0,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/coloquios/{evaluacion_id}/metricas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["convocados"] == 0

    # ---- 8.10: Listado de convocatorias ----

    @pytest.mark.asyncio
    async def test_listar_convocatorias_paginado(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_convocatorias = AsyncMock(return_value={
                "items": [
                    {
                        "id": str(uuid.uuid4()),
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "tipo": "Coloquio",
                        "instancia": "Coloquio Final",
                        "dias_disponibles": 5,
                        "total_convocados": 20,
                        "total_reservas_activas": 10,
                        "total_cupos_libres": 40,
                    }
                ],
                "total": 1,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/coloquios",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["total"] == 1

    @pytest.mark.asyncio
    async def test_listar_convocatorias_vacio(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_convocatorias = AsyncMock(return_value={
                "items": [],
                "total": 0,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/coloquios",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_listar_convocatorias_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/coloquios",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.11: Agenda de reservas ----

    @pytest.mark.asyncio
    async def test_agenda_reservas_ordenada(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener_agenda = AsyncMock(return_value=[
                {
                    "reserva_id": str(uuid.uuid4()),
                    "alumno_nombre": "Juan",
                    "alumno_apellido": "Pérez",
                    "alumno_email": "juan@test.com",
                    "fecha_reserva": "2026-06-15",
                    "hora_reserva": "2026-06-15T10:00:00+00:00",
                }
            ])

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/coloquios/{evaluacion_id}/agenda",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_agenda_sin_reservas_vacio(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener_agenda = AsyncMock(return_value=[])

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/coloquios/{evaluacion_id}/agenda",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json() == []

    @pytest.mark.asyncio
    async def test_agenda_403_sin_permiso(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/coloquios/{evaluacion_id}/agenda",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.12: Cierre de convocatoria ----

    @pytest.mark.asyncio
    async def test_cerrar_convocatoria_exitosa(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.cerrar_convocatoria = AsyncMock(return_value={
                "id": str(evaluacion_id),
                "estado": "Cerrada",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/coloquios/{evaluacion_id}/cerrar",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["estado"] == "Cerrada"

    @pytest.mark.asyncio
    async def test_cerrar_convocatoria_ya_cerrada(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import DomainError
            mock_svc.cerrar_convocatoria = AsyncMock(
                side_effect=DomainError("La convocatoria ya está cerrada")
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/coloquios/{evaluacion_id}/cerrar",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_cerrar_convocatoria_403_sin_permiso(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/coloquios/{evaluacion_id}/cerrar",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.13: Edición de convocatoria ----

    @pytest.mark.asyncio
    async def test_editar_convocatoria_exitosa(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar_convocatoria = AsyncMock(return_value={
                "id": str(evaluacion_id),
                "instancia": "Coloquio Modificado",
                "dias_disponibles": 10,
                "estado": "Activa",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/coloquios/{evaluacion_id}",
                    json={"instancia": "Coloquio Modificado"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["instancia"] == "Coloquio Modificado"

    @pytest.mark.asyncio
    async def test_editar_convocatoria_cerrada_rechaza(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import DomainError
            mock_svc.editar_convocatoria = AsyncMock(
                side_effect=DomainError("No se puede editar una convocatoria cerrada")
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/coloquios/{evaluacion_id}",
                    json={"instancia": "Editada"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 400

    # ---- 8.14: Convocatorias disponibles para alumno ----

    @pytest.mark.asyncio
    async def test_disponibles_lista(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_disponibles = AsyncMock(return_value=[
                {
                    "id": str(uuid.uuid4()),
                    "materia_nombre": "Matemática",
                    "instancia": "Coloquio Final",
                    "tipo": "Coloquio",
                    "dias_restantes_con_cupo": 3,
                }
            ])

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/coloquios/disponibles",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert len(response.json()) == 1

    # ---- 8.15: Tests de auditoría ----

    @pytest.mark.asyncio
    async def test_audit_crear_convocatoria(self):
        evaluacion_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear_convocatoria = AsyncMock(return_value={
                "id": str(evaluacion_id),
                "tipo": "Coloquio",
                "dias_generados": 5,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/coloquios",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "tipo": "Coloquio",
                        "instancia": "Coloquio Final",
                        "dias_disponibles": 5,
                        "cupo_por_dia": 10,
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 201

    # ---- 8.16: Tests de concurrencia ----

    @pytest.mark.asyncio
    async def test_concurrencia_ultimo_cupo(self):
        evaluacion_id = uuid.uuid4()
        dia_id = uuid.uuid4()
        count = 0

        async def reservar_concurrente(*args, **kwargs):
            nonlocal count
            if count > 0:
                from app.core.exceptions import DomainError
                raise DomainError("Cupo agotado para el día seleccionado")
            count += 1
            return {
                "id": str(uuid.uuid4()),
                "evaluacion_dia_id": str(dia_id),
                "fecha_hora": "2026-06-15T10:00:00+00:00",
                "estado": "Activa",
            }

        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.coloquios.ColoquioService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.reservar_turno = AsyncMock(side_effect=reservar_concurrente)

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response1 = await client.post(
                    f"/api/coloquios/{evaluacion_id}/reservar",
                    json={"evaluacion_dia_id": str(dia_id)},
                    headers={"Authorization": "Bearer fake-token"},
                )
                response2 = await client.post(
                    f"/api/coloquios/{evaluacion_id}/reservar",
                    json={"evaluacion_dia_id": str(dia_id)},
                    headers={"Authorization": "Bearer fake-token"},
                )

                assert response1.status_code == 201
                assert response2.status_code == 409
