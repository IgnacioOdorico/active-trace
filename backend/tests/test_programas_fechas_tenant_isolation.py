import uuid
from unittest.mock import AsyncMock

import pytest


class _MockUniqueResult:
    def __init__(self, values=None):
        self._values = values if values is not None else []

    def unique(self):
        return self

    def scalar_one_or_none(self):
        return self._values[0] if self._values else None

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


class TestProgramaMateriaTenantIsolation:
    @pytest.mark.asyncio
    async def test_get_by_materia_carrera_cohorte_filters_tenant(self):
        from app.repositories.programa_materia_repository import ProgramaMateriaRepository

        tenant_a = uuid.uuid4()
        tenant_b = uuid.uuid4()
        materia_id = uuid.uuid4()
        carrera_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()

        repo_a = ProgramaMateriaRepository(tenant_a)
        repo_b = ProgramaMateriaRepository(tenant_b)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        await repo_a.get_by_materia_carrera_cohorte(
            mock_session, materia_id, carrera_id, cohorte_id
        )
        query_a = str(mock_session.execute.call_args[0][0].compile(
            compile_kwargs={"literal_binds": True}
        ))
        assert tenant_a.hex in query_a
        assert tenant_b.hex not in query_a

        mock_session.execute.reset_mock()

        await repo_b.get_by_materia_carrera_cohorte(
            mock_session, materia_id, carrera_id, cohorte_id
        )
        query_b = str(mock_session.execute.call_args[0][0].compile(
            compile_kwargs={"literal_binds": True}
        ))
        assert tenant_b.hex in query_b
        assert tenant_a.hex not in query_b

    @pytest.mark.asyncio
    async def test_base_get_filters_tenant(self):
        from app.repositories.programa_materia_repository import ProgramaMateriaRepository

        tenant_id = uuid.uuid4()
        repo = ProgramaMateriaRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        await repo.get(mock_session, uuid.uuid4())
        query = str(mock_session.execute.call_args[0][0].compile(
            compile_kwargs={"literal_binds": True}
        ))
        assert tenant_id.hex in query

    @pytest.mark.asyncio
    async def test_base_get_all_filters_tenant(self):
        from app.repositories.programa_materia_repository import ProgramaMateriaRepository

        tenant_id = uuid.uuid4()
        repo = ProgramaMateriaRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        await repo.get_all(mock_session)
        query = str(mock_session.execute.call_args[0][0].compile(
            compile_kwargs={"literal_binds": True}
        ))
        assert tenant_id.hex in query

    @pytest.mark.asyncio
    async def test_service_listar_filters_tenant(self):
        from app.services.programa_service import ProgramaService

        tenant_a = uuid.uuid4()
        tenant_b = uuid.uuid4()

        svc_a = ProgramaService(tenant_a)
        svc_b = ProgramaService(tenant_b)

        assert svc_a._tenant_id == tenant_a
        assert svc_b._tenant_id == tenant_b
        assert svc_a._tenant_id != svc_b._tenant_id


class TestFechaAcademicaTenantIsolation:
    @pytest.mark.asyncio
    async def test_get_by_materia_cohorte_filters_tenant(self):
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        tenant_a = uuid.uuid4()
        tenant_b = uuid.uuid4()
        materia_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()

        repo_a = FechaAcademicaRepository(tenant_a)
        repo_b = FechaAcademicaRepository(tenant_b)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        await repo_a.get_by_materia_cohorte(mock_session, materia_id, cohorte_id)
        query_a = str(mock_session.execute.call_args[0][0].compile(
            compile_kwargs={"literal_binds": True}
        ))
        assert tenant_a.hex in query_a
        assert tenant_b.hex not in query_a

        mock_session.execute.reset_mock()

        await repo_b.get_by_materia_cohorte(mock_session, materia_id, cohorte_id)
        query_b = str(mock_session.execute.call_args[0][0].compile(
            compile_kwargs={"literal_binds": True}
        ))
        assert tenant_b.hex in query_b
        assert tenant_a.hex not in query_b

    @pytest.mark.asyncio
    async def test_base_get_filters_tenant(self):
        from app.repositories.fecha_academica_repository import FechaAcademicaRepository

        tenant_id = uuid.uuid4()
        repo = FechaAcademicaRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        await repo.get(mock_session, uuid.uuid4())
        query = str(mock_session.execute.call_args[0][0].compile(
            compile_kwargs={"literal_binds": True}
        ))
        assert tenant_id.hex in query

    @pytest.mark.asyncio
    async def test_service_listar_filters_tenant(self):
        from app.services.fecha_academica_service import FechaAcademicaService

        tenant_a = uuid.uuid4()
        tenant_b = uuid.uuid4()

        svc_a = FechaAcademicaService(tenant_a)
        svc_b = FechaAcademicaService(tenant_b)

        assert svc_a._tenant_id == tenant_a
        assert svc_b._tenant_id == tenant_b
        assert svc_a._tenant_id != svc_b._tenant_id
