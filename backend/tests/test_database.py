import pytest
from sqlalchemy import text


pytestmark = pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)


@pytest.mark.asyncio
async def test_db_select_one(db_session):
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar_one()
    assert value == 1
