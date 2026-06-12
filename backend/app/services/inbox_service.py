import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.mensaje import Mensaje
from app.repositories.mensaje_repository import MensajeRepository


class InboxService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._repo = MensajeRepository(tenant_id)
        self._tenant_id = tenant_id

    async def listar_hilos(
        self,
        db: AsyncSession,
        usuario_id: uuid.UUID,
        pagina: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        items, total = await self._repo.listar_hilos(
            db, usuario_id, pagina=pagina, page_size=page_size
        )
        result = [self._serializar_resumen(m) for m in items]
        return result, total

    async def obtener_hilo(
        self,
        db: AsyncSession,
        usuario_id: uuid.UUID,
        hilo_id: uuid.UUID,
    ) -> dict:
        mensajes = await self._repo.obtener_hilo(db, hilo_id)
        if not mensajes:
            raise EntityNotFoundError("Mensaje", hilo_id)

        raiz = mensajes[0]
        if raiz.remitente_id != usuario_id and raiz.destinatario_id != usuario_id:
            raise EntityNotFoundError("Mensaje", hilo_id)

        respuestas = [self._serializar(m) for m in mensajes[1:]]
        result = self._serializar(raiz)
        result["respuestas"] = respuestas
        return result

    async def responder(
        self,
        db: AsyncSession,
        usuario_id: uuid.UUID,
        hilo_id: uuid.UUID,
        cuerpo: str,
    ) -> dict:
        mensajes = await self._repo.obtener_hilo(db, hilo_id)
        if not mensajes:
            raise EntityNotFoundError("Mensaje", hilo_id)

        raiz = mensajes[0]
        if raiz.remitente_id != usuario_id and raiz.destinatario_id != usuario_id:
            raise EntityNotFoundError("Mensaje", hilo_id)

        # Swap: who replies becomes the new remitente, the other becomes destinatario
        destinatario_id = (
            raiz.remitente_id if raiz.destinatario_id == usuario_id
            else raiz.destinatario_id
        )

        reply = await self._repo.responder(
            db,
            remitente_id=usuario_id,
            destinatario_id=destinatario_id,
            thread_id=hilo_id,
            asunto=f"Re: {raiz.asunto}",
            cuerpo=cuerpo,
        )

        return self._serializar(reply)

    @staticmethod
    def _serializar_resumen(m: Mensaje) -> dict:
        return {
            "id": str(m.id),
            "remitente_id": str(m.remitente_id),
            "destinatario_id": str(m.destinatario_id),
            "asunto": m.asunto,
            "ultimo_mensaje": m.cuerpo,
            "leido": m.leido,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }

    @staticmethod
    def _serializar(m: Mensaje) -> dict:
        return {
            "id": str(m.id),
            "thread_id": str(m.thread_id) if m.thread_id else None,
            "remitente_id": str(m.remitente_id),
            "destinatario_id": str(m.destinatario_id),
            "asunto": m.asunto,
            "cuerpo": m.cuerpo,
            "leido": m.leido,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
