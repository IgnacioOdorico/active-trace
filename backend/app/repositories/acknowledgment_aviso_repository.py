import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.repositories.base import BaseRepository


class AcknowledgmentAvisoRepository(BaseRepository[AcknowledgmentAviso]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(AcknowledgmentAviso, tenant_id)

    async def contar_por_aviso(
        self, session: AsyncSession, aviso_id: uuid.UUID
    ) -> int:
        query = select(func.count()).select_from(AcknowledgmentAviso).where(
            AcknowledgmentAviso.tenant_id == self._tenant_id,
            AcknowledgmentAviso.deleted_at.is_(None),
            AcknowledgmentAviso.aviso_id == aviso_id,
        )
        result = await session.execute(query)
        return result.scalar_one()

    async def existe(
        self, session: AsyncSession, aviso_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> bool:
        query = select(AcknowledgmentAviso).where(
            AcknowledgmentAviso.tenant_id == self._tenant_id,
            AcknowledgmentAviso.deleted_at.is_(None),
            AcknowledgmentAviso.aviso_id == aviso_id,
            AcknowledgmentAviso.usuario_id == usuario_id,
        )
        result = await session.execute(query)
        return result.unique().scalar_one_or_none() is not None

    async def crear(
        self,
        session: AsyncSession,
        aviso_id: uuid.UUID,
        usuario_id: uuid.UUID,
    ) -> AcknowledgmentAviso:
        data = {
            "aviso_id": aviso_id,
            "usuario_id": usuario_id,
            "confirmado_at": datetime.now(timezone.utc),
        }
        return await self.create(session, data)
