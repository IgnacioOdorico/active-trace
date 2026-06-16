"""
Bootstrap inicial del sistema.

Crea el tenant demo y el usuario admin por defecto.
Uso: python -m app.core.bootstrap
"""

import asyncio
import os

from sqlalchemy import select

from app.core import database as db_module
from app.core.auth import hash_password
from app.core.config import Settings
from app.models.rol import Rol
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_rol import UserRol

ADMIN_EMAIL = os.getenv("BOOTSTRAP_EMAIL", "admin@demo.local")
ADMIN_PASSWORD = os.getenv("BOOTSTRAP_PASSWORD", "Admin1234!")
TENANT_SLUG = os.getenv("BOOTSTRAP_TENANT_SLUG", "demo")
TENANT_NAME = os.getenv("BOOTSTRAP_TENANT_NAME", "Demo UTN")


async def main() -> None:
    settings = Settings()
    db_module.init_db(settings.DATABASE_URL)

    factory = db_module.async_session_factory
    if factory is None:
        raise RuntimeError("Database not initialized")

    async with factory() as db:
        existing = (await db.execute(select(User).where(User.email == ADMIN_EMAIL))).scalar_one_or_none()
        if existing:
            print(f"⚠️  El usuario {ADMIN_EMAIL} ya existe. No se creó nada.")
            return

        tenant = Tenant(slug=TENANT_SLUG, name=TENANT_NAME)
        db.add(tenant)
        await db.flush()

        user = User(
            tenant_id=tenant.id,
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            is_active=True,
        )
        db.add(user)
        await db.flush()

        rol = (await db.execute(select(Rol).where(Rol.codigo == "ADMIN"))).scalar_one()
        db.add(UserRol(user_id=user.id, rol_id=rol.id))
        await db.commit()

        print(f"✅ Tenant:   {TENANT_NAME} (slug: {TENANT_SLUG})")
        print(f"✅ Usuario:  {ADMIN_EMAIL}")
        print(f"✅ Password: {ADMIN_PASSWORD}")
        print()
        print("Podés cambiar estas credenciales con las variables de entorno:")
        print("  BOOTSTRAP_EMAIL, BOOTSTRAP_PASSWORD, BOOTSTRAP_TENANT_SLUG, BOOTSTRAP_TENANT_NAME")


if __name__ == "__main__":
    asyncio.run(main())
