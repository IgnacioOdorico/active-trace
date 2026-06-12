"""Entrypoint principal del worker.

Arranca ComunicacionWorker y cualquier otro worker futuro.
"""

import asyncio
import logging
import os
import signal

from app.core.config import Settings
from app.core.database import close_db, init_db
from app.core import database as db_module
from app.workers.comunicacion_worker import ComunicacionWorker

logger = logging.getLogger(__name__)

settings = Settings()


async def main() -> None:
    init_db(settings.DATABASE_URL)
    if db_module.async_session_factory is None:
        raise RuntimeError("Database not initialized")

    poll_interval = int(os.getenv("WORKER_POLL_INTERVAL", "10"))

    worker = ComunicacionWorker(
        session_factory=db_module.async_session_factory,
        poll_interval=poll_interval,
    )

    logger.info(
        "Worker starting with poll_interval=%ss", poll_interval
    )

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        logger.info("Received SIGTERM, shutting down...")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _signal_handler)

    worker_task = asyncio.create_task(worker.run())

    try:
        await stop_event.wait()
    except asyncio.CancelledError:
        pass
    finally:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        await close_db()
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
