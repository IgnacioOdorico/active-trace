"""
Orquestador del seed data de activia-trace.

Crea datos de prueba para (casi) todo el dominio: carreras, materias,
cohortes, padrón, calificaciones, usuarios de cada rol, equipos/asignaciones,
avisos, comunicaciones, encuentros, guardias, coloquios, tareas, fechas
académicas, programas de materia y auditoría.

Liquidaciones (salarios, plus, facturas) queda fuera a propósito: ese
módulo está bloqueado por preguntas de producto abiertas (PA-22/PA-23,
ver knowledge-base/10_preguntas_abiertas.md) y no se simula data de
ejemplo hasta que se cierren.

Uso: python -m app.core.seed_data
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import database as db_module
from app.core.config import Settings
from app.core.seed_demo.academico import seed_academico
from app.core.seed_demo.auditoria import seed_auditoria
from app.core.seed_demo.coloquios import seed_coloquios
from app.core.seed_demo.comunicacion import seed_comunicacion
from app.core.seed_demo.encuentros import seed_encuentros
from app.core.seed_demo.estructura import seed_estructura
from app.core.seed_demo.tareas import seed_tareas
from app.core.seed_demo.usuarios import DEMO_PASSWORD, seed_usuarios
from app.models.user import User


async def get_admin(db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where(User.email == "admin@demo.local")
    )
    user = result.unique().scalar_one_or_none()
    if not user:
        raise RuntimeError("admin@demo.local not found. Run regular seed first.")
    return user


async def seed() -> None:
    settings = Settings()
    db_module.init_db(settings.DATABASE_URL)

    factory = db_module.async_session_factory
    if factory is None:
        raise RuntimeError("Database not initialized")

    async with factory() as db:
        admin = await get_admin(db)
        tenant_id = admin.tenant_id
        now = datetime.now(timezone.utc)

        ctx = await seed_academico(db, admin, tenant_id, now)
        usuarios, asignaciones_extra = await seed_usuarios(db, tenant_id, ctx)
        await seed_comunicacion(db, tenant_id, admin, ctx, now)
        await seed_encuentros(db, tenant_id, ctx, asignaciones_extra)
        await seed_coloquios(db, tenant_id, ctx, usuarios)
        await seed_tareas(db, tenant_id, admin, ctx, usuarios)
        await seed_estructura(db, tenant_id, ctx, now)
        await seed_auditoria(db, tenant_id, admin, ctx)

        await db.commit()

        print("\n✅ Seed data creada exitosamente:\n")
        for codigo, _ in ctx["carreras_data"]:
            print(f"  Carrera: {codigo}")
        for codigo, nombre, _ in ctx["materias_data"]:
            print(f"  Materia: {codigo} - {nombre}")
        print("  Cohorte: 2026")
        print(f"  Alumnos (padrón): {len(ctx['alumnos'])}")
        for codigo in ctx["materias"]:
            print(f"  Entradas Padrón ({codigo}): {len(ctx['entrada_ids'].get(codigo, []))}")
        print(f"  Asignaciones admin: {len(ctx['asignaciones'])} (PROFESOR en todas las materias)")
        print("  Umbral: PROG1 configurado (60%)")
        print()
        print("  Usuarios de prueba por rol (password para todos: " + DEMO_PASSWORD + "):")
        for codigo_rol, user in usuarios.items():
            print(f"    {codigo_rol}: {user.email}")
        print()
        print("  Avisos: 2 (1 global con ack, 1 por materia)")
        print("  Comunicaciones: 4 (Nueva, Enviado, Error, Cancelado)")
        print("  Encuentros: 1 slot recurrente + 1 instancia realizada")
        print("  Guardias: 1 (Matemática I, pendiente)")
        print("  Coloquios: 1 evaluación con día, reserva y resultado")
        print("  Tareas: 3 (Pendiente, En progreso, Resuelta) + 1 comentario")
        print("  Fecha académica: 1 (Parcial 1, Programación I)")
        print("  Programa de materia: 1 (Programación I)")
        print("  Audit log: 4 entradas de ejemplo")
        print()
        print("  ⚠️  Liquidaciones (salarios/plus/facturas): omitido a propósito,")
        print("      módulo bloqueado por PA-22/PA-23 (ver knowledge-base/10_preguntas_abiertas.md)")
        print()
