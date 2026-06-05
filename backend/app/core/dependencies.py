from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()


# RESERVADO: get_current_user → C-03 (JWT token validation + Argon2id)
# RESERVADO: get_tenant → C-02 (tenant resolution from header/domain)
# RESERVADO: require_permission → C-04 (RBAC check against permission matrix)
