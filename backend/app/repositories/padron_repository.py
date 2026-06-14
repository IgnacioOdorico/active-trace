import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entrada_padron import EntradaPadron
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository


class VersionPadronRepository(BaseRepository[VersionPadron]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(VersionPadron, tenant_id)

    async def get_active(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
    ) -> VersionPadron | None:
        query = self._base_query().where(
            self._model.materia_id == materia_id,
            self._model.cohorte_id == cohorte_id,
            self._model.activa,
        )
        result = await session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_active_by_materia(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
    ) -> Sequence[VersionPadron]:
        query = self._base_query().where(
            self._model.materia_id == materia_id,
            self._model.activa,
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def deactivate_all(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
    ) -> None:
        query = (
            update(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.cohorte_id == cohorte_id,
                self._model.activa,
                self._model.deleted_at.is_(None),
            )
            .values(activa=False)
        )
        await session.execute(query)

    async def soft_delete_by_materia(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
    ) -> None:
        now = datetime.now(timezone.utc)
        query = (
            update(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.deleted_at.is_(None),
            )
            .values(deleted_at=now)
        )
        await session.execute(query)


class EntradaPadronRepository(BaseRepository[EntradaPadron]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(EntradaPadron, tenant_id)

    async def bulk_create(
        self,
        session: AsyncSession,
        entradas: list[EntradaPadron],
    ) -> list[EntradaPadron]:
        session.add_all(entradas)
        await session.flush()
        for e in entradas:
            await session.refresh(e)
        return entradas

    async def get_by_version(
        self,
        session: AsyncSession,
        version_id: uuid.UUID,
    ) -> Sequence[EntradaPadron]:
        query = self._base_query().where(
            self._model.version_id == version_id
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def soft_delete_by_materia(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
    ) -> None:
        now = datetime.now(timezone.utc)
        subquery = (
            select(VersionPadron.id)
            .where(
                VersionPadron.tenant_id == self._tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.deleted_at.is_(None),
            )
        )
        query = (
            update(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.deleted_at.is_(None),
                self._model.version_id.in_(subquery),
            )
            .values(deleted_at=now)
        )
        await session.execute(query)
