import asyncio
import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.comunicacion_service import ComunicacionService

logger = logging.getLogger(__name__)


class MockProveedorEnvio:
    def __init__(self, debe_fallar: bool = False) -> None:
        self._debe_fallar = debe_fallar
        self.enviados = 0

    async def enviar(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        if self._debe_fallar:
            raise RuntimeError("Simulated error")
        self.enviados += 1


class ComunicacionWorker:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        poll_interval: int | None = None,
    ) -> None:
        self._db_session_factory = session_factory
        self._poll_interval = poll_interval or int(
            os.getenv("WORKER_POLL_INTERVAL", "10")
        )
        self._running = False
        self._service: ComunicacionService | None = None

    def _init_service(self, tenant_id):
        self._service = ComunicacionService(tenant_id)

    async def _iteracion(self) -> None:
        if self._service is None or self._db_session_factory is None:
            return
        async with self._db_session_factory() as db:
            proveedor = MockProveedorEnvio()
            resultado = await self._service.procesar_cola(db, proveedor)
            if resultado["procesadas"] > 0:
                logger.info("Cola procesada: %s", resultado)

    async def run(self) -> None:
        self._running = True
        logger.info(
            "ComunicacionWorker iniciado (intervalo=%ss)", self._poll_interval
        )
        try:
            while self._running:
                await self._iteracion()
                await asyncio.sleep(self._poll_interval)
        except asyncio.CancelledError:
            logger.info("ComunicacionWorker detenido por señal")
            self._running = False
        except Exception:
            logger.exception("Error en ComunicacionWorker")
            self._running = False
