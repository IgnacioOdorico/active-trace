import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mensaje import Mensaje
from app.repositories.base import BaseRepository


class MensajeRepository(BaseRepository[Mensaje]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Mensaje, tenant_id)

    async def listar_hilos(
        self,
        session: AsyncSession,
        usuario_id: uuid.UUID,
        pagina: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Mensaje], int]:
        base = (
            select(Mensaje)
            .where(
                Mensaje.tenant_id == self._tenant_id,
                Mensaje.deleted_at.is_(None),
                Mensaje.destinatario_id == usuario_id,
                Mensaje.thread_id.is_(None),
            )
            .order_by(Mensaje.created_at.desc())
        )

        count_q = base.with_only_columns(func.count())
        total_result = await session.execute(count_q)
        total = total_result.scalar_one()

        page_q = base.offset((pagina - 1) * page_size).limit(page_size)
        result = await session.execute(page_q)
        items = list(result.unique().scalars().all())

        return items, total

    async def obtener_hilo(
        self,
        session: AsyncSession,
        hilo_id: uuid.UUID,
    ) -> list[Mensaje]:
        query = (
            select(Mensaje)
            .where(
                Mensaje.tenant_id == self._tenant_id,
                Mensaje.deleted_at.is_(None),
                (Mensaje.id == hilo_id) | (Mensaje.thread_id == hilo_id),
            )
            .order_by(Mensaje.created_at.asc())
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def responder(
        self,
        session: AsyncSession,
        remitente_id: uuid.UUID,
        destinatario_id: uuid.UUID,
        thread_id: uuid.UUID,
        asunto: str,
        cuerpo: str,
    ) -> Mensaje:
        data = {
            "remitente_id": remitente_id,
            "destinatario_id": destinatario_id,
            "thread_id": thread_id,
            "asunto": asunto,
            "cuerpo": cuerpo,
            "leido": False,
        }
        return await self.create(session, data)
