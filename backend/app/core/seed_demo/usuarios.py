"""Un usuario adicional por cada rol del dominio, con su asignación docente.

El email queda en texto plano a propósito: el login real
(app/api/v1/routers/auth.py) compara User.email contra el valor recibido
sin desencriptar, igual que el admin creado por bootstrap.py. DNI/CUIL/CBU
sí se cifran (AES-256), como exige la regla dura de PII del proyecto.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.core.security import encrypt
from app.models.asignacion import Asignacion
from app.models.rol import Rol
from app.models.user import User
from app.models.user_rol import UserRol

DEMO_PASSWORD = "Demo1234!"

# (codigo_rol, email, nombre, apellidos, dni, cuil)
_USUARIOS_DEMO = [
    ("PROFESOR", "profesor1@demo.local", "Marina", "Suárez", "30111222", "27-30111222-4"),
    ("COORDINADOR", "coordinador1@demo.local", "Diego", "Herrera", "28222333", "20-28222333-1"),
    ("TUTOR", "tutor1@demo.local", "Patricia", "Núñez", "31333444", "27-31333444-7"),
    ("ALUMNO", "alumno1@demo.local", "Lucía", "Fernández", "41444555", "27-41444555-2"),
    ("NEXO", "nexo1@demo.local", "Roberto", "Acosta", "29555666", "20-29555666-9"),
    ("FINANZAS", "finanzas1@demo.local", "Carla", "Medina", "32666777", "27-32666777-5"),
]


async def _get_or_create_user(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    email: str,
    nombre: str,
    apellidos: str,
    dni: str,
    cuil: str,
) -> User:
    existing = await db.execute(
        select(User).where(
            User.tenant_id == tenant_id,
            User.email == email,
            User.deleted_at.is_(None),
        )
    )
    user = existing.unique().scalar_one_or_none()
    if user is None:
        user = User(
            tenant_id=tenant_id,
            email=email,
            hashed_password=hash_password(DEMO_PASSWORD),
            is_active=True,
            nombre=nombre,
            apellidos=apellidos,
            dni=encrypt(dni),
            cuil=encrypt(cuil),
            facturador=False,
            estado="Activo",
        )
        db.add(user)
        await db.flush()
    return user


async def _ensure_rol(db: AsyncSession, user: User, codigo_rol: str) -> None:
    rol_result = await db.execute(select(Rol).where(Rol.codigo == codigo_rol))
    rol = rol_result.unique().scalar_one()

    existing = await db.execute(
        select(UserRol).where(UserRol.user_id == user.id, UserRol.rol_id == rol.id)
    )
    if existing.unique().scalar_one_or_none() is None:
        db.add(UserRol(user_id=user.id, rol_id=rol.id))


async def _ensure_asignacion(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    usuario_id: uuid.UUID,
    rol: str,
    materia_id: uuid.UUID | None,
    carrera_id: uuid.UUID | None,
    cohorte_id: uuid.UUID,
) -> uuid.UUID:
    existing = await db.execute(
        select(Asignacion).where(
            Asignacion.tenant_id == tenant_id,
            Asignacion.usuario_id == usuario_id,
            Asignacion.rol == rol,
            Asignacion.deleted_at.is_(None),
        )
    )
    asignacion = existing.unique().scalar_one_or_none()
    if asignacion is None:
        asignacion = Asignacion(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            rol=rol,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            comisiones=["A"] if materia_id else None,
            desde=datetime(2026, 1, 1, tzinfo=timezone.utc),
            hasta=datetime(2026, 12, 31, tzinfo=timezone.utc),
        )
        db.add(asignacion)
        await db.flush()
    return asignacion.id


async def seed_usuarios(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    ctx: dict[str, Any],
) -> tuple[dict[str, User], dict[str, uuid.UUID]]:
    materias = ctx["materias"]
    carreras = ctx["carreras"]
    cohorte = ctx["cohorte"]

    usuarios: dict[str, User] = {}
    for codigo_rol, email, nombre, apellidos, dni, cuil in _USUARIOS_DEMO:
        user = await _get_or_create_user(db, tenant_id, email, nombre, apellidos, dni, cuil)
        await _ensure_rol(db, user, codigo_rol)
        usuarios[codigo_rol] = user
    await db.flush()

    asignaciones_extra: dict[str, uuid.UUID] = {}
    asignaciones_extra["PROFESOR"] = await _ensure_asignacion(
        db, tenant_id, usuarios["PROFESOR"].id, "PROFESOR",
        materias["ING1"].id, carreras["TUP"].id, cohorte.id,
    )
    asignaciones_extra["TUTOR"] = await _ensure_asignacion(
        db, tenant_id, usuarios["TUTOR"].id, "TUTOR",
        materias["MAT1"].id, carreras["TUP"].id, cohorte.id,
    )
    asignaciones_extra["COORDINADOR"] = await _ensure_asignacion(
        db, tenant_id, usuarios["COORDINADOR"].id, "COORDINADOR",
        None, carreras["TUP"].id, cohorte.id,
    )

    return usuarios, asignaciones_extra
