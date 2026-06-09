import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings
from app.core.database import Base
from app.models.asignacion import Asignacion  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.base import EntityMeta  # noqa: F401
from app.models.calificacion import Calificacion  # noqa: F401
from app.models.carrera import Carrera  # noqa: F401
from app.models.cohorte import Cohorte  # noqa: F401
from app.models.entrada_padron import EntradaPadron  # noqa: F401
from app.models.materia import Materia  # noqa: F401
from app.models.permiso import Permiso  # noqa: F401
from app.models.recovery_token import RecoveryToken  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.rol import Rol  # noqa: F401
from app.models.rol_permiso import RolPermiso  # noqa: F401
from app.models.tenant import Tenant  # noqa: F401
from app.models.umbral_materia import UmbralMateria  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.user_rol import UserRol  # noqa: F401
from app.models.version_padron import VersionPadron  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

settings = Settings()
database_url = settings.DATABASE_URL


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = create_async_engine(database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
