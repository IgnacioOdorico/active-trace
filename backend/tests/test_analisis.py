import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.main import app
from app.models.user import User


class TestCalificacionRepositoryNuevos:
    def _make_session_mock(self, return_value):
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.unique.return_value.all.return_value = return_value
        mock_session.execute = AsyncMock(return_value=mock_result)
        return mock_session

    @pytest.mark.asyncio
    async def test_get_by_materia_con_entrada_joins_entrada(self):
        from app.repositories.calificacion_repository import CalificacionRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        repo = CalificacionRepository(tenant_id)

        mock_session = self._make_session_mock([
            (Mock(entrada_padron_id=uuid.uuid4()), Mock(nombre="Juan"))
        ])

        result = await repo.get_by_materia_con_entrada(mock_session, materia_id)

        assert len(result) == 1
        assert result[0][1].nombre == "Juan"

    @pytest.mark.asyncio
    async def test_get_estado_por_materia_returns_data(self):
        from app.repositories.calificacion_repository import CalificacionRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        repo = CalificacionRepository(tenant_id)

        mock_session = self._make_session_mock([
            (Mock(aprobado=True), Mock(nombre="Maria"))
        ])

        result = await repo.get_estado_por_materia(mock_session, materia_id)

        assert len(result) == 1
        assert result[0][1].nombre == "Maria"

    @pytest.mark.asyncio
    async def test_get_ranking_aprobadas_returns_counts(self):
        from app.repositories.calificacion_repository import CalificacionRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()
        repo = CalificacionRepository(tenant_id)

        mock_session = self._make_session_mock([
            (entrada_id, 5)
        ])

        result = await repo.get_ranking_aprobadas(mock_session, materia_id)

        assert len(result) == 1
        assert result[0][1] == 5

    @pytest.mark.asyncio
    async def test_get_ranking_aprobadas_empty(self):
        from app.repositories.calificacion_repository import CalificacionRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        repo = CalificacionRepository(tenant_id)

        mock_session = self._make_session_mock([])

        result = await repo.get_ranking_aprobadas(mock_session, materia_id)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_notas_por_alumno_returns_data(self):
        from app.repositories.calificacion_repository import CalificacionRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        repo = CalificacionRepository(tenant_id)

        mock_session = self._make_session_mock([
            (Mock(nombre_actividad="TP1", nota_numerica=80.0), Mock(nombre="Ana"))
        ])

        result = await repo.get_notas_por_alumno(
            mock_session, materia_id, ["TP1", "TP2"]
        )

        assert len(result) == 1
        assert result[0][0].nombre_actividad == "TP1"

    @pytest.mark.asyncio
    async def test_get_filtrado_applies_filters(self):
        from app.repositories.calificacion_repository import CalificacionRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        repo = CalificacionRepository(tenant_id)

        mock_session = AsyncMock()
        mock_result_count = Mock()
        mock_result_count.scalar_one.return_value = 1
        mock_result_items = Mock()
        mock_result_items.unique.return_value.all.return_value = [
            (Mock(aprobado=True), Mock(nombre="Luis", comision="A"))
        ]

        mock_session.execute = AsyncMock(
            side_effect=[mock_result_count, mock_result_items]
        )

        items, total = await repo.get_filtrado(
            mock_session,
            materia_id=materia_id,
            comision="A",
            pagina=1,
            por_pagina=50,
        )

        assert total == 1
        assert len(items) == 1

    @pytest.mark.asyncio
    async def test_get_filtrado_with_q_search(self):
        from app.repositories.calificacion_repository import CalificacionRepository
        tenant_id = uuid.uuid4()
        repo = CalificacionRepository(tenant_id)

        mock_session = AsyncMock()
        mock_result_count = Mock()
        mock_result_count.scalar_one.return_value = 0
        mock_result_items = Mock()
        mock_result_items.unique.return_value.all.return_value = []
        mock_session.execute = AsyncMock(
            side_effect=[mock_result_count, mock_result_items]
        )

        items, total = await repo.get_filtrado(
            mock_session,
            q="Juan",
            pagina=1,
            por_pagina=50,
        )

        assert total == 0
        assert len(items) == 0


class TestAnalisisService:
    @pytest.mark.asyncio
    async def test_atrasados_sin_actividades_es_atrasado(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.analisis_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = uuid.uuid4()
            mock_entrada.nombre = "Juan"
            mock_entrada.apellidos = "Perez"
            mock_entrada.email = "juan@test.com"
            mock_entrada.comision = "A"

            MockEntradaRepo.return_value.get_by_version = AsyncMock(
                return_value=[mock_entrada]
            )
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[AsyncMock(id=uuid.uuid4())]
            )
            MockCalifRepo.return_value.get_by_materia = AsyncMock(return_value=[])
            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            result = await svc.atrasados(AsyncMock(), materia_id)

            assert len(result) == 1
            assert result[0]["nombre"] == "Juan"
            assert any(
                p["motivo"] == "actividades_faltantes"
                for p in result[0]["actividades_problematicas"]
            )

    @pytest.mark.asyncio
    async def test_atrasados_nota_inferior_umbral(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.analisis_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.nombre = "Maria"
            mock_entrada.apellidos = "Garcia"
            mock_entrada.email = "maria@test.com"
            mock_entrada.comision = "B"

            MockEntradaRepo.return_value.get_by_version = AsyncMock(
                return_value=[mock_entrada]
            )
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[AsyncMock(id=uuid.uuid4())]
            )

            mock_calif = AsyncMock()
            mock_calif.entrada_padron_id = entrada_id
            mock_calif.nombre_actividad = "TP1"
            mock_calif.nota_numerica = 40.0
            mock_calif.nota_textual = None
            mock_calif.aprobado = False
            MockCalifRepo.return_value.get_by_materia = AsyncMock(
                return_value=[mock_calif]
            )

            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            result = await svc.atrasados(AsyncMock(), materia_id)

            assert len(result) == 1
            assert any(
                p["motivo"] == "nota_inferior_umbral"
                for p in result[0]["actividades_problematicas"]
            )

    @pytest.mark.asyncio
    async def test_atrasados_aprobado_no_aparece(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.analisis_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.nombre = "Carlos"
            mock_entrada.apellidos = "Lopez"
            mock_entrada.email = "carlos@test.com"
            mock_entrada.comision = "A"

            MockEntradaRepo.return_value.get_by_version = AsyncMock(
                return_value=[mock_entrada]
            )
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[AsyncMock(id=uuid.uuid4())]
            )

            mock_calif = AsyncMock()
            mock_calif.entrada_padron_id = entrada_id
            mock_calif.nombre_actividad = "TP1"
            mock_calif.nota_numerica = 85.0
            mock_calif.nota_textual = None
            mock_calif.aprobado = True
            MockCalifRepo.return_value.get_by_materia = AsyncMock(
                return_value=[mock_calif]
            )

            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            result = await svc.atrasados(AsyncMock(), materia_id)

            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_atrasados_sin_padron_activo_raise(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository"),
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[]
            )

            svc = AnalisisService(tenant_id)
            with pytest.raises(DomainError, match="No hay un padrón activo"):
                await svc.atrasados(AsyncMock(), materia_id)

    @pytest.mark.asyncio
    async def test_atrasados_umbral_por_defecto_60(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.analisis_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.nombre = "Ana"
            mock_entrada.apellidos = "Martinez"
            mock_entrada.email = "ana@test.com"
            mock_entrada.comision = "C"

            MockEntradaRepo.return_value.get_by_version = AsyncMock(
                return_value=[mock_entrada]
            )
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[AsyncMock(id=uuid.uuid4())]
            )

            mock_calif = AsyncMock()
            mock_calif.entrada_padron_id = entrada_id
            mock_calif.nombre_actividad = "TP1"
            mock_calif.nota_numerica = 50.0
            mock_calif.nota_textual = None
            mock_calif.aprobado = False
            MockCalifRepo.return_value.get_by_materia = AsyncMock(
                return_value=[mock_calif]
            )

            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            result = await svc.atrasados(AsyncMock(), materia_id)

            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_ranking_solo_aprobadas(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id_1 = uuid.uuid4()
        entrada_id_2 = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.analisis_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada_1 = AsyncMock()
            mock_entrada_1.id = entrada_id_1
            mock_entrada_1.nombre = "Luis"
            mock_entrada_1.apellidos = "Gomez"
            mock_entrada_1.comision = "A"

            mock_entrada_2 = AsyncMock()
            mock_entrada_2.id = entrada_id_2
            mock_entrada_2.nombre = "Sofia"
            mock_entrada_2.apellidos = "Diaz"
            mock_entrada_2.comision = "B"

            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[AsyncMock(id=uuid.uuid4())]
            )
            MockEntradaRepo.return_value.get_by_version = AsyncMock(
                return_value=[mock_entrada_1, mock_entrada_2]
            )

            MockCalifRepo.return_value.get_ranking_aprobadas = AsyncMock(
                return_value=[(entrada_id_1, 3)]
            )
            MockCalifRepo.return_value.get_by_materia = AsyncMock(return_value=[
                Mock(entrada_padron_id=entrada_id_1, aprobado=True),
                Mock(entrada_padron_id=entrada_id_1, aprobado=True),
                Mock(entrada_padron_id=entrada_id_1, aprobado=True),
                Mock(entrada_padron_id=entrada_id_2, aprobado=False),
                Mock(entrada_padron_id=entrada_id_2, aprobado=False),
            ])

            svc = AnalisisService(tenant_id)
            result = await svc.ranking(AsyncMock(), materia_id)

            assert len(result) == 1
            assert result[0]["nombre"] == "Luis"
            assert result[0]["actividades_aprobadas"] == 3

    @pytest.mark.asyncio
    async def test_ranking_vacio_sin_aprobadas(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            MockCalifRepo.return_value.get_ranking_aprobadas = AsyncMock(
                return_value=[]
            )

            svc = AnalisisService(tenant_id)
            result = await svc.ranking(AsyncMock(), materia_id)

            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_notas_finales_promedio_correcto(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.nombre = "Pedro"
            mock_entrada.apellidos = "Ramirez"
            mock_entrada.comision = "A"

            mock_calif_1 = AsyncMock()
            mock_calif_1.entrada_padron_id = entrada_id
            mock_calif_1.nombre_actividad = "TP1"
            mock_calif_1.nota_numerica = 80.0
            mock_calif_1.nota_textual = None

            mock_calif_2 = AsyncMock()
            mock_calif_2.entrada_padron_id = entrada_id
            mock_calif_2.nombre_actividad = "TP2"
            mock_calif_2.nota_numerica = 90.0
            mock_calif_2.nota_textual = None

            MockCalifRepo.return_value.get_notas_por_alumno = AsyncMock(
                return_value=[
                    (mock_calif_1, mock_entrada),
                    (mock_calif_2, mock_entrada),
                ]
            )
            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            actividades = [("TP1", "numerica"), ("TP2", "numerica")]
            result = await svc.notas_finales(
                AsyncMock(), materia_id, actividades
            )

            assert len(result) == 1
            assert result[0]["nombre"] == "Pedro"
            assert result[0]["nota_final"] == 85.0
            assert result[0]["estado"] == "aprobado"

    @pytest.mark.asyncio
    async def test_notas_finales_textuales_excluidas_promedio(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.nombre = "Laura"
            mock_entrada.apellidos = "Fernandez"
            mock_entrada.comision = "B"

            mock_calif_num = AsyncMock()
            mock_calif_num.entrada_padron_id = entrada_id
            mock_calif_num.nombre_actividad = "TP1"
            mock_calif_num.nota_numerica = 75.0
            mock_calif_num.nota_textual = None

            mock_calif_text = AsyncMock()
            mock_calif_text.entrada_padron_id = entrada_id
            mock_calif_text.nombre_actividad = "Participacion"
            mock_calif_text.nota_numerica = None
            mock_calif_text.nota_textual = "Satisfactorio"

            MockCalifRepo.return_value.get_notas_por_alumno = AsyncMock(
                return_value=[
                    (mock_calif_num, mock_entrada),
                    (mock_calif_text, mock_entrada),
                ]
            )
            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            actividades = [("TP1", "numerica"), ("Participacion", "textual")]
            result = await svc.notas_finales(
                AsyncMock(), materia_id, actividades
            )

            assert len(result) == 1
            assert result[0]["nota_final"] == 75.0
            assert "Participacion" in result[0]["actividades_textuales"]
            assert result[0]["estado"] == "aprobado"

    @pytest.mark.asyncio
    async def test_notas_finales_estado_no_aprobado_bajo_umbral(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.nombre = "Marco"
            mock_entrada.apellidos = "Diaz"
            mock_entrada.comision = "A"

            mock_calif = AsyncMock()
            mock_calif.entrada_padron_id = entrada_id
            mock_calif.nombre_actividad = "TP1"
            mock_calif.nota_numerica = 40.0
            mock_calif.nota_textual = None

            MockCalifRepo.return_value.get_notas_por_alumno = AsyncMock(
                return_value=[(mock_calif, mock_entrada)]
            )
            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            actividades = [("TP1", "numerica")]
            result = await svc.notas_finales(
                AsyncMock(), materia_id, actividades
            )

            assert result[0]["nota_final"] == 40.0
            assert result[0]["estado"] == "no_aprobado"

    @pytest.mark.asyncio
    async def test_notas_finales_sin_notas_numericas_estado_no_aprobado(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.nombre = "Sol"
            mock_entrada.apellidos = "Vega"
            mock_entrada.comision = "A"

            mock_calif_text = AsyncMock()
            mock_calif_text.entrada_padron_id = entrada_id
            mock_calif_text.nombre_actividad = "Participacion"
            mock_calif_text.nota_numerica = None
            mock_calif_text.nota_textual = "Satisfactorio"

            MockCalifRepo.return_value.get_notas_por_alumno = AsyncMock(
                return_value=[(mock_calif_text, mock_entrada)]
            )
            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            actividades = [("Participacion", "textual")]
            result = await svc.notas_finales(
                AsyncMock(), materia_id, actividades
            )

            assert result[0]["nota_final"] is None
            assert result[0]["estado"] == "no_aprobado"

    @pytest.mark.asyncio
    async def test_notas_finales_actividad_no_encontrada_422(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            MockCalifRepo.return_value.get_notas_por_alumno = AsyncMock(
                return_value=[]
            )

            svc = AnalisisService(tenant_id)
            actividades = [("ActividadInexistente", "numerica")]
            with pytest.raises(DomainError, match="Actividad no encontrada"):
                await svc.notas_finales(
                    AsyncMock(), materia_id, actividades
                )

    @pytest.mark.asyncio
    async def test_reportes_rapidos_returns_metrics(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_a = uuid.uuid4()
        entrada_b = uuid.uuid4()
        entrada_c = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.analisis_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.analisis_service.AuditLogService"),
        ):
            calificaciones = [
                Mock(entrada_padron_id=entrada_a, nombre_actividad="TP1", nota_numerica=80.0, aprobado=True),
                Mock(entrada_padron_id=entrada_a, nombre_actividad="TP2", nota_numerica=90.0, aprobado=True),
                Mock(entrada_padron_id=entrada_b, nombre_actividad="TP1", nota_numerica=40.0, aprobado=False),
            ]
            MockCalifRepo.return_value.get_by_materia = AsyncMock(return_value=calificaciones)

            mock_entradas = [
                Mock(id=entrada_a), Mock(id=entrada_b), Mock(id=entrada_c),
            ]
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[Mock(id=uuid.uuid4())]
            )
            MockEntradaRepo.return_value.get_by_version = AsyncMock(
                return_value=mock_entradas
            )
            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            result = await svc.reportes_rapidos(AsyncMock(), materia_id)

            # entrada_a: 2/2 aprobadas. entrada_b: nota inferior al umbral -> atrasado.
            # entrada_c: sin calificaciones -> atrasado. Solo entrada_a queda "aprobado".
            assert result["total_alumnos"] == 3
            assert result["total_calificaciones"] == 3
            assert result["alumnos_atrasados_count"] == 2
            assert result["alumnos_aprobados_count"] == 1
            assert result["promedio_aprobacion_general"] == pytest.approx(66.67, abs=0.01)

    @pytest.mark.asyncio
    async def test_reportes_rapidos_aprobados_no_es_negativo_con_alumnos_sin_notas(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_con_notas = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.analisis_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.analisis_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.analisis_service.AuditLogService"),
        ):
            calificaciones = [
                Mock(entrada_padron_id=entrada_con_notas, nombre_actividad="TP1", nota_numerica=80.0, aprobado=True),
            ]
            MockCalifRepo.return_value.get_by_materia = AsyncMock(return_value=calificaciones)

            # 4 entradas en el padrón, pero solo 1 tiene calificaciones cargadas.
            mock_entradas = [Mock(id=entrada_con_notas)] + [Mock(id=uuid.uuid4()) for _ in range(3)]
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[Mock(id=uuid.uuid4())]
            )
            MockEntradaRepo.return_value.get_by_version = AsyncMock(
                return_value=mock_entradas
            )
            MockUmbralRepo.return_value.get_by_materia = AsyncMock(return_value=None)
            MockUmbralRepo.return_value.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = AnalisisService(tenant_id)
            result = await svc.reportes_rapidos(AsyncMock(), materia_id)

            assert result["alumnos_aprobados_count"] >= 0
            assert result["alumnos_aprobados_count"] == 1
            assert result["alumnos_atrasados_count"] == 3

    @pytest.mark.asyncio
    async def test_reportes_sin_datos(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            MockCalifRepo.return_value.get_by_materia = AsyncMock(return_value=[])

            svc = AnalisisService(tenant_id)
            result = await svc.reportes_rapidos(AsyncMock(), materia_id)

            assert result["sin_datos"] is True
            assert result["total_calificaciones"] == 0

    @pytest.mark.asyncio
    async def test_exportar_tps_genera_xlsx(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.nombre = "Test"
            mock_entrada.apellidos = "Alumno"

            MockEntradaRepo.return_value.get_by_version = AsyncMock(
                return_value=[mock_entrada]
            )

            mock_calif = AsyncMock()
            mock_calif.entrada_padron_id = entrada_id
            mock_calif.nombre_actividad = "TP Final"
            mock_calif.nota_numerica = None
            mock_calif.nota_textual = "Entregado"
            mock_calif.aprobado = True

            MockCalifRepo.return_value.get_by_materia_con_entrada = AsyncMock(
                return_value=[(mock_calif, mock_entrada)]
            )

            svc = AnalisisService(tenant_id)
            result = await svc.exportar_tps(AsyncMock(), materia_id)

            assert "content_type" in result
            assert result["content_type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    @pytest.mark.asyncio
    async def test_exportar_tps_sin_entregas_retorna_json(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            MockCalifRepo.return_value.get_by_materia_con_entrada = AsyncMock(
                return_value=[]
            )

            svc = AnalisisService(tenant_id)
            result = await svc.exportar_tps(AsyncMock(), materia_id)

            assert result["total"] == 0
            assert "mensaje" in result

    @pytest.mark.asyncio
    async def test_exportar_tps_solo_textuales(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.nombre = "Test"
            mock_entrada.apellidos = "Alumno"

            MockEntradaRepo.return_value.get_by_version = AsyncMock(
                return_value=[mock_entrada]
            )

            calif_textual = AsyncMock()
            calif_textual.entrada_padron_id = entrada_id
            calif_textual.nombre_actividad = "TP Textual"
            calif_textual.nota_numerica = None
            calif_textual.nota_textual = "Entregado"
            calif_textual.aprobado = True

            calif_numerica = AsyncMock()
            calif_numerica.entrada_padron_id = entrada_id
            calif_numerica.nombre_actividad = "TP Numerico"
            calif_numerica.nota_numerica = 85.0
            calif_numerica.nota_textual = None
            calif_numerica.aprobado = True

            MockCalifRepo.return_value.get_by_materia_con_entrada = AsyncMock(
                return_value=[(calif_textual, mock_entrada), (calif_numerica, mock_entrada)]
            )

            svc = AnalisisService(tenant_id)
            result = await svc.exportar_tps(AsyncMock(), materia_id)

            assert result["total"] > 0
            assert "content_type" in result

    @pytest.mark.asyncio
    async def test_monitor_general_paginado(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_item = (Mock(aprobado=True, nombre_actividad="TP1"), Mock(
                nombre="Juan", apellidos="Perez", email="j@test.com",
                comision="A", regional="CABA"))
            MockCalifRepo.return_value.get_filtrado = AsyncMock(
                return_value=([mock_item], 1)
            )

            svc = AnalisisService(tenant_id)
            result = await svc.monitor_general(
                AsyncMock(), pagina=1, por_pagina=50
            )

            assert result["total"] == 1
            assert result["pagina"] == 1
            assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_monitor_general_filtro_materia(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_item = (Mock(aprobado=True, nombre_actividad="TP1"), Mock(
                nombre="Ana", apellidos="Lopez", email="ana@test.com",
                comision="B", regional="BSAS"))
            MockCalifRepo.return_value.get_filtrado = AsyncMock(
                return_value=([mock_item], 1)
            )

            svc = AnalisisService(tenant_id)
            result = await svc.monitor_general(
                AsyncMock(), materia_id=materia_id
            )

            assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_monitor_seguimiento_scope_profesor(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            mock_item = (Mock(aprobado=True, nombre_actividad="TP1", materia_id=uuid.uuid4()), Mock(
                nombre="Luis", apellidos="Garcia", email="luis@test.com",
                comision="A", regional="CABA"))
            MockCalifRepo.return_value.get_filtrado = AsyncMock(
                return_value=([mock_item], 1)
            )

            svc = AnalisisService(tenant_id)
            result = await svc.monitor_seguimiento(
                AsyncMock(),
                materias_ids=[uuid.uuid4()],
            )

            assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_monitor_seguimiento_filtro_comision(self):
        from app.services.analisis_service import AnalisisService
        tenant_id = uuid.uuid4()

        with (
            patch("app.services.analisis_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.analisis_service.UmbralRepository"),
            patch("app.services.analisis_service.VersionPadronRepository"),
            patch("app.services.analisis_service.EntradaPadronRepository"),
            patch("app.services.analisis_service.AuditLogService"),
        ):
            MockCalifRepo.return_value.get_filtrado = AsyncMock(
                return_value=([], 0)
            )

            svc = AnalisisService(tenant_id)
            result = await svc.monitor_seguimiento(
                AsyncMock(),
                comision="A",
                materias_ids=[uuid.uuid4()],
            )

            assert result["total"] == 0


class _MockSession:
    def __init__(self) -> None:
        execute_result = Mock()
        execute_result.scalar_one.return_value = 0
        self.execute = AsyncMock(return_value=execute_result)


class TestMonitorSeguimientoRouter:
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

    @pytest.mark.asyncio
    async def test_reenvia_materia_id_y_actividad_minima_al_service(self):
        materia_id = uuid.uuid4()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.analisis.AnalisisService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.monitor_seguimiento = AsyncMock(return_value={
                "items": [], "total": 0, "pagina": 1, "por_pagina": 50, "total_paginas": 0,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/analisis/monitor-seguimiento",
                    params={
                        "materia_id": str(materia_id),
                        "actividad_minima": "TP1",
                        "desde": "2024-03-01",
                        "hasta": "2024-03-31",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

                _, kwargs = mock_svc.monitor_seguimiento.call_args
                assert kwargs["materias_ids"] == [materia_id]
                assert kwargs["actividad_minima"] == "TP1"
                assert kwargs["desde"] is not None
                assert kwargs["hasta"] is not None

    @pytest.mark.asyncio
    async def test_sin_materia_id_no_filtra_por_materia(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.analisis.AnalisisService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.monitor_seguimiento = AsyncMock(return_value={
                "items": [], "total": 0, "pagina": 1, "por_pagina": 50, "total_paginas": 0,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/analisis/monitor-seguimiento",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

                _, kwargs = mock_svc.monitor_seguimiento.call_args
                assert kwargs["materias_ids"] is None
                assert kwargs["actividad_minima"] is None


db = pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)


@pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)
class TestAnalisisEndpoints:
    @pytest.mark.asyncio
    async def test_atrasados_returns_200(self, async_client, auth_header):
        materia_id = str(uuid.uuid4())
        with patch("app.routers.analisis.AnalisisService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.atrasados = AsyncMock(return_value=[
                {
                    "entrada_padron_id": str(uuid.uuid4()),
                    "nombre": "Juan",
                    "apellidos": "Perez",
                    "email": "juan@test.com",
                    "comision": "A",
                    "actividades_problematicas": [
                        {"nombre_actividad": "TP1", "motivo": "actividades_faltantes"}
                    ],
                }
            ])
            response = await async_client.get(
                f"/api/analisis/atrasados/{materia_id}",
                headers=auth_header,
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["nombre"] == "Juan"

    @pytest.mark.asyncio
    async def test_atrasados_sin_permiso_403(self, async_client):
        mock_auth = {"sub": str(uuid.uuid4()), "tenant_id": str(uuid.uuid4()), "rols": []}
        with patch("app.core.auth.decode_access_token", return_value=mock_auth):
            response = await async_client.get(
                f"/api/analisis/atrasados/{uuid.uuid4()}",
                headers={"Authorization": "Bearer no-perms"},
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_ranking_returns_200(self, async_client, auth_header):
        materia_id = str(uuid.uuid4())
        with patch("app.routers.analisis.AnalisisService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.ranking = AsyncMock(return_value=[
                {
                    "entrada_padron_id": str(uuid.uuid4()),
                    "nombre": "Luis",
                    "apellidos": "Gomez",
                    "comision": "A",
                    "actividades_aprobadas": 3,
                    "total_actividades": 5,
                }
            ])
            response = await async_client.get(
                f"/api/analisis/ranking/{materia_id}",
                headers=auth_header,
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["actividades_aprobadas"] == 3

    @pytest.mark.asyncio
    async def test_reportes_returns_200(self, async_client, auth_header):
        materia_id = str(uuid.uuid4())
        with patch("app.routers.analisis.AnalisisService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.reportes_rapidos = AsyncMock(return_value={
                "total_alumnos": 10,
                "total_actividades": 5,
                "total_calificaciones": 50,
                "promedio_aprobacion_general": 0.75,
                "alumnos_atrasados_count": 2,
                "alumnos_aprobados_count": 8,
                "sin_datos": False,
            })
            response = await async_client.get(
                f"/api/analisis/reportes/{materia_id}",
                headers=auth_header,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["total_calificaciones"] == 50

    @pytest.mark.asyncio
    async def test_notas_finales_returns_200(self, async_client, auth_header):
        with patch("app.routers.analisis.AnalisisService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.notas_finales = AsyncMock(return_value=[
                {
                    "entrada_padron_id": str(uuid.uuid4()),
                    "nombre": "Pedro",
                    "apellidos": "Ramirez",
                    "comision": "A",
                    "notas": [
                        {"actividad": "TP1", "nota_numerica": 80.0, "nota_textual": None},
                    ],
                    "nota_final": 80.0,
                    "actividades_textuales": [],
                    "estado": "aprobado",
                }
            ])
            response = await async_client.post(
                "/api/analisis/notas-finales",
                json={"materia_id": str(uuid.uuid4()), "actividades": ["TP1", "TP2"]},
                headers=auth_header,
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    @pytest.mark.asyncio
    async def test_exportar_tps_returns_200(self, async_client, auth_header):
        materia_id = str(uuid.uuid4())
        with patch("app.routers.analisis.AnalisisService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.exportar_tps = AsyncMock(return_value={
                "total": 0,
                "mensaje": "No se encontraron entregas sin corregir",
            })
            response = await async_client.get(
                f"/api/analisis/exportar-tps/{materia_id}",
                headers=auth_header,
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_monitor_general_returns_200(self, async_client, auth_header):
        with patch("app.routers.analisis.AnalisisService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.monitor_general = AsyncMock(return_value={
                "items": [
                    {
                        "entrada_padron_id": str(uuid.uuid4()),
                        "nombre": "Juan",
                        "apellidos": "Perez",
                        "email": "juan@test.com",
                        "comision": "A",
                        "regional": "CABA",
                        "materia_id": None,
                        "total_actividades": 5,
                        "aprobadas": 3,
                        "estado": "atrasado",
                    }
                ],
                "total": 1,
                "pagina": 1,
                "por_pagina": 50,
                "total_paginas": 1,
            })
            response = await async_client.get(
                "/api/analisis/monitor-general",
                headers=auth_header,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_monitor_seguimiento_returns_200(self, async_client, auth_header):
        with patch("app.routers.analisis.AnalisisService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.monitor_seguimiento = AsyncMock(return_value={
                "items": [],
                "total": 0,
                "pagina": 1,
                "por_pagina": 50,
                "total_paginas": 0,
            })
            response = await async_client.get(
                "/api/analisis/monitor-seguimiento",
                headers=auth_header,
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_exportar_tps_403_sin_permiso(self, async_client):
        mock_auth = {"sub": str(uuid.uuid4()), "tenant_id": str(uuid.uuid4()), "rols": []}
        with patch("app.core.auth.decode_access_token", return_value=mock_auth):
            response = await async_client.get(
                f"/api/analisis/exportar-tps/{uuid.uuid4()}",
                headers={"Authorization": "Bearer no-perms"},
            )
            assert response.status_code == 403


@pytest.fixture
def auth_header():
    mock_user = {"sub": str(uuid.uuid4()), "tenant_id": str(uuid.uuid4()), "rols": ["COORDINADOR"]}
    with patch("app.core.auth.decode_access_token", return_value=mock_user):
        yield {"Authorization": "Bearer fake-token"}


@pytest.fixture
def async_client():
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
