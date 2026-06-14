import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import DomainError
from app.services.liquidaciones import LiquidacionService


def _make_mock_result(rows: list | None = None, scalar=None):
    m = MagicMock()
    if rows is not None:
        m.unique().scalars().all.return_value = rows
    if scalar is not None:
        m.scalar_one.return_value = scalar
    return m


class TestCalcularLiquidacion:
    @pytest.fixture
    def service(self):
        return LiquidacionService(tenant_id=uuid.uuid4())

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_calcular_periodo_cerrado_raise_error(self, service, mock_session):
        service._repo.periodo_cerrado = AsyncMock(return_value=True)
        with pytest.raises(DomainError, match="ya está cerrado"):
            await service.calcular(mock_session, uuid.uuid4(), "2026-06")

    @pytest.mark.asyncio
    async def test_calcular_sin_comisiones_retorna_vacio(self, service, mock_session):
        service._repo.periodo_cerrado = AsyncMock(return_value=False)
        mock_result = _make_mock_result(rows=[])

        async def execute_side(*args, **kwargs):
            return mock_result

        mock_session.execute.side_effect = execute_side
        result = await service.calcular(
            mock_session, uuid.uuid4(), "2026-06"
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_get_salario_base_vigente_none(self, service, mock_session):
        mock_result = MagicMock()
        mock_result.unique().scalar_one_or_none.return_value = None

        async def execute_side(*args, **kwargs):
            return mock_result

        mock_session.execute.side_effect = execute_side
        result = await service._get_salario_base_vigente(
            mock_session, "PROFESOR", date(2026, 6, 1)
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_get_salario_plus_vigente_none(self, service, mock_session):
        mock_result = MagicMock()
        mock_result.unique().scalar_one_or_none.return_value = None

        async def execute_side(*args, **kwargs):
            return mock_result

        mock_session.execute.side_effect = execute_side
        result = await service._get_salario_plus_vigente(
            mock_session, "PROG", "PROFESOR", date(2026, 6, 1)
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_cerrar_liquidacion(self, service, mock_session):
        mock_liq = MagicMock()
        mock_liq.id = uuid.uuid4()
        mock_liq.estado = "Cerrada"
        service._repo.cerrar = AsyncMock(return_value=mock_liq)
        result = await service.cerrar(mock_session, mock_liq.id)
        assert result["estado"] == "Cerrada"

    @pytest.mark.asyncio
    async def test_cerrar_liquidacion_ya_cerrada(self, service, mock_session):
        service._repo.cerrar = AsyncMock(
            side_effect=DomainError(
                detail="La liquidación ya está cerrada",
                context={},
            )
        )
        with pytest.raises(DomainError, match="ya está cerrada"):
            await service.cerrar(mock_session, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_listar_por_periodo(self, service, mock_session):
        mock_liq = MagicMock()
        mock_liq.id = uuid.uuid4()
        mock_liq.cohorte_id = uuid.uuid4()
        mock_liq.periodo = "2026-06"
        mock_liq.usuario_id = uuid.uuid4()
        mock_liq.rol = "PROFESOR"
        mock_liq.comisiones = ["PROG"]
        mock_liq.monto_base = 500.0
        mock_liq.monto_plus = 200.0
        mock_liq.total = 700.0
        mock_liq.es_nexo = False
        mock_liq.excluido_por_factura = False
        mock_liq.estado = "Abierta"
        service._repo.listar_por_periodo = AsyncMock(return_value=[mock_liq])
        result = await service.listar(mock_session, "2026-06")
        assert len(result) == 1
        assert result[0]["total"] == 700.0

    @pytest.mark.asyncio
    async def test_obtener_kpis(self, service, mock_session):
        service._repo.obtener_kpis = AsyncMock(
            return_value={
                "total_general": 1000.0,
                "total_nexo": 500.0,
                "total_facturas_pendientes": 0.0,
                "total_facturas_abonadas": 0.0,
                "cantidad_docentes_general": 2,
                "cantidad_docentes_nexo": 1,
                "cantidad_docentes_facturantes": 0,
            }
        )
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0

        async def execute_side(*args, **kwargs):
            return mock_result

        mock_session.execute.side_effect = execute_side
        kpis = await service.obtener_kpis(mock_session, "2026-06")
        assert kpis["total_general"] == 1000.0
        assert kpis["cantidad_docentes_general"] == 2
