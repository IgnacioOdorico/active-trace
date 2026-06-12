import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import DomainError
from app.repositories.factura import FacturaRepository


class TestFacturaRepository:
    @pytest.fixture
    def repo(self):
        return FacturaRepository(tenant_id=uuid.uuid4())

    @pytest.mark.asyncio
    async def test_abonar_factura_pendiente(self, repo):
        mock_session = AsyncMock()
        mock_factura = MagicMock()
        mock_factura.estado = "Pendiente"
        mock_factura.abonada_at = None
        mock_factura.id = uuid.uuid4()
        repo.get = AsyncMock(return_value=mock_factura)
        result = await repo.abonar(mock_session, uuid.uuid4())
        assert result.estado == "Abonada"
        assert result.abonada_at is not None

    @pytest.mark.asyncio
    async def test_abonar_factura_ya_abonada_raise(self, repo):
        mock_session = AsyncMock()
        mock_factura = MagicMock()
        mock_factura.estado = "Abonada"
        repo.get = AsyncMock(return_value=mock_factura)
        with pytest.raises(DomainError, match="ya está abonada"):
            await repo.abonar(mock_session, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_listar_por_periodo(self, repo):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.unique().scalars().all.return_value = []
        mock_session.execute.return_value = mock_result
        result = await repo.listar_por_filtros(mock_session, periodo="2026-06")
        assert result == []

    @pytest.mark.asyncio
    async def test_listar_por_estado(self, repo):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.unique().scalars().all.return_value = []
        mock_session.execute.return_value = mock_result
        result = await repo.listar_por_filtros(mock_session, estado="Pendiente")
        assert result == []
