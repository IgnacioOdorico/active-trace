import uuid
from unittest.mock import AsyncMock, Mock

import pytest

from app.models.guardia import Guardia
from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.slot_encuentro import SlotEncuentro
from app.repositories.base import BaseRepository


class _MockUniqueResult:
    def __init__(self, values=None):
        self._values = values if values is not None else []

    def unique(self):
        return self

    def scalars(self):
        return _MockScalars(self._values)

    def scalar_one(self):
        return 3


class _MockScalars:
    def __init__(self, values=None):
        self._values = values if values is not None else []

    def all(self):
        return self._values

    def first(self):
        return self._values[0] if self._values else None

    def one_or_none(self):
        return self._values[0] if self._values else None

    def one(self):
        if not self._values:
            raise ValueError("No result")
        return self._values[0]


class TestSlotEncuentroRepository:
    def test_extends_base_repository(self):
        from app.repositories.slot_encuentro_repository import SlotEncuentroRepository
        assert issubclass(SlotEncuentroRepository, BaseRepository)

    def test_uses_slot_encuentro_model(self):
        from app.repositories.slot_encuentro_repository import SlotEncuentroRepository
        repo = SlotEncuentroRepository(uuid.uuid4())
        assert repo._model is SlotEncuentro


class TestInstanciaEncuentroRepository:
    def test_extends_base_repository(self):
        from app.repositories.instancia_encuentro_repository import InstanciaEncuentroRepository
        assert issubclass(InstanciaEncuentroRepository, BaseRepository)

    def test_uses_instancia_encuentro_model(self):
        from app.repositories.instancia_encuentro_repository import InstanciaEncuentroRepository
        repo = InstanciaEncuentroRepository(uuid.uuid4())
        assert repo._model is InstanciaEncuentro

    @pytest.mark.asyncio
    async def test_get_by_slot(self):
        from app.repositories.instancia_encuentro_repository import InstanciaEncuentroRepository
        tenant_id = uuid.uuid4()
        slot_id = uuid.uuid4()
        repo = InstanciaEncuentroRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        result = await repo.get_by_slot(mock_session, slot_id)

        assert result == []
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert slot_id.hex in compiled
        assert tenant_id.hex in compiled

    @pytest.mark.asyncio
    async def test_get_by_materia_filtros(self):
        from app.repositories.instancia_encuentro_repository import InstanciaEncuentroRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        repo = InstanciaEncuentroRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        result = await repo.get_by_materia_filtros(
            mock_session, materia_id=materia_id, fecha_desde=None, fecha_hasta=None, estado=None
        )

        assert result == []
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert materia_id.hex in compiled

    @pytest.mark.asyncio
    async def test_get_by_materia_filtros_with_fechas(self):
        from app.repositories.instancia_encuentro_repository import InstanciaEncuentroRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        repo = InstanciaEncuentroRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        from datetime import date
        await repo.get_by_materia_filtros(
            mock_session,
            materia_id=materia_id,
            fecha_desde=date(2026, 3, 1),
            fecha_hasta=date(2026, 6, 30),
            estado="Cancelado",
        )

        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert "Cancelado" in compiled
        assert materia_id.hex in compiled


class TestGuardiaRepository:
    def test_extends_base_repository(self):
        from app.repositories.guardia_repository import GuardiaRepository
        assert issubclass(GuardiaRepository, BaseRepository)

    def test_uses_guardia_model(self):
        from app.repositories.guardia_repository import GuardiaRepository
        repo = GuardiaRepository(uuid.uuid4())
        assert repo._model is Guardia

    @pytest.mark.asyncio
    async def test_get_by_asignacion(self):
        from app.repositories.guardia_repository import GuardiaRepository
        tenant_id = uuid.uuid4()
        asignacion_id = uuid.uuid4()
        repo = GuardiaRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        result = await repo.get_by_asignacion(mock_session, asignacion_id)

        assert result == []
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert asignacion_id.hex in compiled

    @pytest.mark.asyncio
    async def test_get_all_filtros(self):
        from app.repositories.guardia_repository import GuardiaRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        repo = GuardiaRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        result = await repo.get_all_filtros(mock_session, materia_id=materia_id, asignacion_id=None)

        assert result == []
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert materia_id.hex in compiled
