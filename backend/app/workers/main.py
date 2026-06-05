"""RESERVADO para ADR-003: entrypoint mínimo del worker.

La tecnología real de la cola (asyncio propio / Celery / ARQ) se define en ADR-003.
C-01 deja este placeholder no-op para que docker-compose tenga un entrypoint.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Worker started (placeholder — no-op loop)")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Worker shutting down")


if __name__ == "__main__":
    asyncio.run(main())
