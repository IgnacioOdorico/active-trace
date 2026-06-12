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
