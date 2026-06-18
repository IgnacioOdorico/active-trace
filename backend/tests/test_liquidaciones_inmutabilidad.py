import uuid
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import DomainError
from app.repositories.liquidacion import LiquidacionRepository


class TestInmutabilidad:
    @pytest.fixture
    def repo(self):
        return LiquidacionRepository(tenant_id=uuid.uuid4())

    @pytest.mark.asyncio
    async def test_cerrar_liquidacion_ya_cerrada_raise(self, repo):
        mock_session = AsyncMock()
        mock_liq = AsyncMock()
        mock_liq.estado = "Cerrada"
        repo.get = AsyncMock(return_value=mock_liq)
        with pytest.raises(DomainError, match="ya está cerrada"):
            await repo.cerrar(mock_session, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_cerrar_liquidacion_abierta_ok(self, repo):
        mock_session = AsyncMock()
        mock_liq = AsyncMock()
        mock_liq.estado = "Abierta"
        mock_liq.id = uuid.uuid4()
        repo.get = AsyncMock(return_value=mock_liq)
        result = await repo.cerrar(mock_session, uuid.uuid4())
        assert result.estado == "Cerrada"

    @pytest.mark.asyncio
    async def test_validar_no_cerrada_ok(self, repo):
        mock_session = AsyncMock()
        mock_liq = AsyncMock()
        mock_liq.estado = "Abierta"
        repo.get = AsyncMock(return_value=mock_liq)
        result = await repo._validar_no_cerrada(mock_session, uuid.uuid4())
        assert result.estado == "Abierta"

    @pytest.mark.asyncio
    async def test_validar_no_cerrada_closed_raise(self, repo):
        mock_session = AsyncMock()
        mock_liq = AsyncMock()
        mock_liq.estado = "Cerrada"
        repo.get = AsyncMock(return_value=mock_liq)
        with pytest.raises(DomainError, match="cerrada"):
            await repo._validar_no_cerrada(mock_session, uuid.uuid4())


class TestSoftDeleteAbiertas:
    """Recalcular debe reemplazar el borrador: soft-delete de las
    liquidaciones 'Abierta' previas de esa cohorte+período, nunca un
    hard delete (regla dura #13)."""

    @pytest.fixture
    def repo(self):
        return LiquidacionRepository(tenant_id=uuid.uuid4())

    @pytest.mark.asyncio
    async def test_soft_delete_abiertas_ejecuta_update_no_delete(self, repo):
        mock_session = AsyncMock()
        cohorte_id = uuid.uuid4()

        await repo.soft_delete_abiertas(mock_session, cohorte_id, "2026-06")

        mock_session.execute.assert_awaited_once()
        executed_stmt = mock_session.execute.await_args.args[0]
        assert executed_stmt.is_dml
        assert type(executed_stmt).__name__ == "Update"

    @pytest.mark.asyncio
    async def test_base_query_excluye_soft_deleted(self, repo):
        query = repo._base_query()
        compiled = str(query)
        assert "deleted_at IS NULL" in compiled
