"""
Script de seed data para activia-trace.

La implementación vive en app/core/seed_demo/ (un módulo por dominio).
Nota: existe también app/core/seed.py (SEED_ROLES/PERMISO_DESCRIPTIONS,
catálogo de roles y permisos) — son cosas distintas, no confundir.

Uso: python -m app.core.seed_data
"""

import asyncio

from app.core.seed_demo import seed

if __name__ == "__main__":
    asyncio.run(seed())
