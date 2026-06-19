import uuid

import pytest

from app.repositories.tarea_repository import TareaRepository


class _FakeScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one(self):
        return self._value

    def unique(self):
        return self

    def scalars(self):
        return self

    def all(self):
        return []


class _FakeSession:
    """Captures executed statements without hitting a real DB."""

    def __init__(self):
        self.executed_statements = []

    async def execute(self, statement):
        self.executed_statements.append(statement)
        return _FakeScalarResult(0)


class TestTareaRepositoryCountQuery:
    @pytest.mark.asyncio
    async def test_list_mias_count_query_has_no_order_by(self):
        repo = TareaRepository(uuid.uuid4())
        session = _FakeSession()

        await repo.list_mias(session, usuario_id=uuid.uuid4())

        count_stmt = session.executed_statements[0]
        compiled = str(count_stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "ORDER BY" not in compiled.upper()

    @pytest.mark.asyncio
    async def test_list_todas_count_query_has_no_order_by(self):
        repo = TareaRepository(uuid.uuid4())
        session = _FakeSession()

        await repo.list_todas(session)

        count_stmt = session.executed_statements[0]
        compiled = str(count_stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "ORDER BY" not in compiled.upper()
