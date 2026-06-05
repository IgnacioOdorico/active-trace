from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


async_session_factory: async_sessionmaker[AsyncSession] | None = None
_engine: AsyncEngine | None = None


def init_db(database_url: str) -> None:
    global _engine, async_session_factory
    _engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )
    async_session_factory = async_sessionmaker(
        _engine, expire_on_commit=False
    )


async def close_db() -> None:
    global _engine, async_session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    async_session_factory = None
