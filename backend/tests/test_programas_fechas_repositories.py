import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.fecha_academica import FechaAcademica
from app.models.programa_materia import ProgramaMateria
from app.repositories.base import BaseRepository


class _MockUniqueResult:
    def __init__(self, values=None):
        self._values = values if values is not None else []

    def unique(self):
        return self

    def scalars(self):
        return _MockScalars(self._values)

    def scalar_one(self):
        return 0


class _MockScalars:
    def __init__(self, values=None):
        self._values = values if values is not None else []

    def all(self):
        return self._values

    def one_or_none(self):
        return self._values[0] if self._values else None

    def first(self):
        return self._values[0] if self._values else None


class TestProgramaMateriaRepository:
    def test_extends_base_repository(self):
        from app.repositories.programa_materia_repository import ProgramaMateriaRepository
        assert issubclass(ProgramaMateriaRepository, BaseRepository)

    def test_uses_programa_materia_model(self):
        from app.repositories.programa_materia_repository import ProgramaMateriaRepository
        repo = ProgramaMateriaRepository(uuid.uuid4())
        assert repo._model is ProgramaMateria

    @pytest.mark.asyncio
    async def test_get_by_materia_carrera_cohorte(self):
        from app.repositories.programa_materia_repository import ProgramaMateriaRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        carrera_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()
        repo = ProgramaMateriaRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        result = await repo.get_by_materia_carrera_cohorte(
            mock_session, materia_id, carrera_id, cohorte_id
        )

        assert result == []
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert materia_id.hex in compiled
        assert carrera_id.hex in compiled
        assert cohorte_id.hex in compiled
        assert tenant_id.hex in compiled


class TestFechaAcademicaRepository:
    def test_extends_base_repository(self):
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository
        assert issubclass(FechaAcademicaRepository, BaseRepository)

    def test_uses_fecha_academica_model(self):
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository
        repo = FechaAcademicaRepository(uuid.uuid4())
        assert repo._model is FechaAcademica

    @pytest.mark.asyncio
    async def test_get_by_materia_cohorte(self):
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()
        repo = FechaAcademicaRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        result = await repo.get_by_materia_cohorte(
            mock_session, materia_id, cohorte_id
        )

        assert result == []
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert materia_id.hex in compiled
        assert cohorte_id.hex in compiled
        assert tenant_id.hex in compiled
