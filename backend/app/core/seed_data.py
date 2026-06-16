"""
Script de seed data para activia-trace.

Crea datos de prueba: carreras, materias, cohortes, versiones de padrón,
entradas de padrón (alumnos), asignaciones, calificaciones y umbrales.

Uso: python -m app.core.seed_data
"""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core import database as db_module
from app.models.asignacion import Asignacion
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.umbral_materia import UmbralMateria
from app.models.user import User
from app.models.user_rol import UserRol
from app.models.rol import Rol
from app.models.version_padron import VersionPadron


async def get_admin(db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where(User.email == "admin@demo.local")
    )
    user = result.unique().scalar_one_or_none()
    if not user:
        raise RuntimeError("admin@demo.local not found. Run regular seed first.")
    return user


async def seed():
    settings = Settings()
    db_module.init_db(settings.DATABASE_URL)

    factory = db_module.async_session_factory
    if factory is None:
        raise RuntimeError("Database not initialized")

    async with factory() as db:
        admin = await get_admin(db)
        tenant_id = admin.tenant_id
        now = datetime.now(timezone.utc)

        # --- Carreras ---
        carreras_data = [
            ("TUP", "Tecnicatura Universitaria en Programación"),
            ("TAS", "Tecnicatura Universitaria en Análisis de Sistemas"),
        ]
        for codigo, nombre in carreras_data:
            existing = await db.execute(
                select(Carrera).where(
                    Carrera.tenant_id == tenant_id,
                    Carrera.codigo == codigo,
                    Carrera.deleted_at.is_(None),
                )
            )
            if existing.unique().scalar_one_or_none() is None:
                db.add(Carrera(tenant_id=tenant_id, codigo=codigo, nombre=nombre))
        await db.flush()

        # Fetch created carreras
        carreras = {}
        for codigo, _ in carreras_data:
            result = await db.execute(
                select(Carrera).where(
                    Carrera.tenant_id == tenant_id,
                    Carrera.codigo == codigo,
                    Carrera.deleted_at.is_(None),
                )
            )
            c = result.unique().scalar_one()
            carreras[codigo] = c

        # --- Materias ---
        materias_data = [
            ("PROG1", "Programación I", carreras["TUP"].id),
            ("PROG2", "Programación II", carreras["TUP"].id),
            ("BD1", "Base de Datos I", carreras["TUP"].id),
            ("MAT1", "Matemática I", carreras["TUP"].id),
            ("ING1", "Inglés I", carreras["TUP"].id),
        ]
        for codigo, nombre, carrera_id in materias_data:
            existing = await db.execute(
                select(Materia).where(
                    Materia.tenant_id == tenant_id,
                    Materia.codigo == codigo,
                    Materia.deleted_at.is_(None),
                )
            )
            if existing.unique().scalar_one_or_none() is None:
                db.add(Materia(
                    tenant_id=tenant_id,
                    codigo=codigo,
                    nombre=nombre,
                    carrera_id=carrera_id,
                ))
        await db.flush()

        materias = {}
        for codigo, _, _ in materias_data:
            result = await db.execute(
                select(Materia).where(
                    Materia.tenant_id == tenant_id,
                    Materia.codigo == codigo,
                    Materia.deleted_at.is_(None),
                )
            )
            m = result.unique().scalar_one()
            materias[codigo] = m

        # --- Cohorte ---
        cohorte_result = await db.execute(
            select(Cohorte).where(
                Cohorte.tenant_id == tenant_id,
                Cohorte.nombre == "2026",
                Cohorte.deleted_at.is_(None),
            )
        )
        cohorte = cohorte_result.unique().scalar_one_or_none()
        if cohorte is None:
            cohorte = Cohorte(
                tenant_id=tenant_id,
                nombre="2026",
                carrera_id=carreras["TUP"].id,
                fecha_inicio=datetime(2026, 3, 1, tzinfo=timezone.utc),
                fecha_fin=datetime(2026, 12, 31, tzinfo=timezone.utc),
                activa=True,
            )
            db.add(cohorte)
            await db.flush()

        # --- Versión Padrón ---
        versiones = {}
        for codigo, materia in materias.items():
            existing_v = await db.execute(
                select(VersionPadron).where(
                    VersionPadron.tenant_id == tenant_id,
                    VersionPadron.materia_id == materia.id,
                    VersionPadron.cohorte_id == cohorte.id,
                    VersionPadron.deleted_at.is_(None),
                )
            )
            v = existing_v.unique().scalar_one_or_none()
            if v is None:
                v = VersionPadron(
                    tenant_id=tenant_id,
                    materia_id=materia.id,
                    cohorte_id=cohorte.id,
                    cargado_por=admin.id,
                    activa=True,
                )
                db.add(v)
                await db.flush()
            versiones[codigo] = v

        # --- Entradas Padrón (alumnos) ---
        alumnos = [
            ("Lautaro", "Martínez", "lautaro.martinez@example.com", "A", "Córdoba"),
            ("Camila", "Rodríguez", "camila.rodriguez@example.com", "A", "Córdoba"),
            ("Mateo", "González", "mateo.gonzalez@example.com", "B", "Rosario"),
            ("Valentina", "López", "valentina.lopez@example.com", "B", "Rosario"),
            ("Benjamín", "Fernández", "benjamin.fernandez@example.com", "A", "Mendoza"),
            ("Isabella", "Pérez", "isabella.perez@example.com", "C", "Córdoba"),
            ("Santiago", "García", "santiago.garcia@example.com", "C", "Córdoba"),
            ("Emilia", "Díaz", "emilia.diaz@example.com", "A", "Rosario"),
            ("Nicolás", "Torres", "nicolas.torres@example.com", "B", "Mendoza"),
            ("Josefina", "Sánchez", "josefina.sanchez@example.com", "C", "Mendoza"),
            ("Facundo", "Romero", "facundo.romero@example.com", "A", "Córdoba"),
            ("Agustina", "Álvarez", "agustina.alvarez@example.com", "B", "Rosario"),
        ]

        entrada_ids: dict[str, list[uuid.UUID]] = {}
        for codigo in materias:
            entrada_ids[codigo] = []

        for nombre, apellidos, email, comision, regional in alumnos:
            for codigo, version in versiones.items():
                existing_e = await db.execute(
                    select(EntradaPadron).where(
                        EntradaPadron.tenant_id == tenant_id,
                        EntradaPadron.version_id == version.id,
                        EntradaPadron.email == email,
                        EntradaPadron.deleted_at.is_(None),
                    )
                )
                existing_entry = existing_e.unique().scalar_one_or_none()
                if existing_entry is None:
                    e = EntradaPadron(
                        tenant_id=tenant_id,
                        version_id=version.id,
                        nombre=nombre,
                        apellidos=apellidos,
                        email=email,
                        comision=comision,
                        regional=regional,
                    )
                    db.add(e)
                    await db.flush()
                    entrada_ids[codigo].append(e.id)
                else:
                    entrada_ids[codigo].append(existing_entry.id)

        await db.flush()

        # --- Asignaciones (admin como profesor de todas las materias) ---
        for codigo, materia in materias.items():
            existing_a = await db.execute(
                select(Asignacion).where(
                    Asignacion.tenant_id == tenant_id,
                    Asignacion.usuario_id == admin.id,
                    Asignacion.materia_id == materia.id,
                    Asignacion.deleted_at.is_(None),
                )
            )
            if existing_a.unique().scalar_one_or_none() is None:
                a = Asignacion(
                    tenant_id=tenant_id,
                    usuario_id=admin.id,
                    rol="PROFESOR",
                    materia_id=materia.id,
                    carrera_id=materia.carrera_id,
                    cohorte_id=cohorte.id,
                    comisiones=["A", "B"],
                    desde=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    hasta=datetime(2026, 12, 31, tzinfo=timezone.utc),
                )
                db.add(a)
        await db.flush()

        # Fetch asignaciones and patch carrera_id/cohorte_id if missing (seed re-run)
        asignaciones: dict[str, uuid.UUID] = {}
        for codigo, materia in materias.items():
            result = await db.execute(
                select(Asignacion).where(
                    Asignacion.tenant_id == tenant_id,
                    Asignacion.usuario_id == admin.id,
                    Asignacion.materia_id == materia.id,
                    Asignacion.deleted_at.is_(None),
                )
            )
            a = result.unique().scalar_one_or_none()
            if a:
                asignaciones[codigo] = a.id
                if a.carrera_id is None and materia.carrera_id:
                    a.carrera_id = materia.carrera_id
                if a.cohorte_id is None:
                    a.cohorte_id = cohorte.id
                if a.comisiones is None:
                    a.comisiones = ["A", "B"]
                if a.hasta is None:
                    a.hasta = datetime(2026, 12, 31, tzinfo=timezone.utc)
        await db.flush()

        # --- Umbral para PROG1 ---
        if "PROG1" in asignaciones:
            existing_umbral = await db.execute(
                select(UmbralMateria).where(
                    UmbralMateria.tenant_id == tenant_id,
                    UmbralMateria.asignacion_id == asignaciones["PROG1"],
                    UmbralMateria.deleted_at.is_(None),
                )
            )
            if existing_umbral.unique().scalar_one_or_none() is None:
                u = UmbralMateria(
                    tenant_id=tenant_id,
                    asignacion_id=asignaciones["PROG1"],
                    materia_id=materias["PROG1"].id,
                    umbral_pct=60.0,
                    valores_aprobatorios=["Aprobado", "APROBADO", "8", "9", "10"],
                )
                db.add(u)
        await db.flush()

        # --- Calificaciones ---
        existing_count = await db.execute(
            select(text("count(*)")).select_from(Calificacion).where(
                Calificacion.tenant_id == tenant_id,
                Calificacion.deleted_at.is_(None),
            )
        )
        count = existing_count.scalar_one()
        if count == 0:
            actividades = ["TP1", "TP2", "Parcial 1", "Parcial 2", "Recuperatorio"]
            calificaciones_data: list[dict] = []

            # PROG1 - all alumnos have calificaciones
            for eid in entrada_ids.get("PROG1", []):
                for i, act in enumerate(actividades):
                    nota = 4 + (i * 10) + (hash(str(eid)) % 20)
                    nota_num = max(1, min(10, nota))
                    calificaciones_data.append({
                        "tenant_id": tenant_id,
                        "entrada_padron_id": eid,
                        "materia_id": materias["PROG1"].id,
                        "nombre_actividad": act,
                        "nota_numerica": float(nota_num),
                        "nota_textual": None,
                        "aprobado": nota_num >= 6,
                        "origen": "Seed",
                        "importado_at": now,
                    })

            # BD1 - some alumnos have calificaciones
            for eid in entrada_ids.get("BD1", [])[:8]:
                for i, act in enumerate(actividades[:3]):
                    nota = 5 + (i * 5) + (hash(str(eid)) % 15)
                    nota_num = max(1, min(10, nota))
                    calificaciones_data.append({
                        "tenant_id": tenant_id,
                        "entrada_padron_id": eid,
                        "materia_id": materias["BD1"].id,
                        "nombre_actividad": act,
                        "nota_numerica": float(nota_num),
                        "nota_textual": None,
                        "aprobado": nota_num >= 6,
                        "origen": "Seed",
                        "importado_at": now,
                    })

            # PROG2 - textual activities
            for eid in entrada_ids.get("PROG2", [])[:6]:
                for i, act in enumerate(["TP1", "TP2"]):
                    valores = ["Entregado", "Aprobado", "Aprobado", "Pendiente"]
                    valor = valores[(hash(str(eid)) + i) % len(valores)]
                    calificaciones_data.append({
                        "tenant_id": tenant_id,
                        "entrada_padron_id": eid,
                        "materia_id": materias["PROG2"].id,
                        "nombre_actividad": act,
                        "nota_numerica": None,
                        "nota_textual": valor,
                        "aprobado": valor == "Aprobado",
                        "origen": "Seed",
                        "importado_at": now,
                    })

            for cd in calificaciones_data:
                db.add(Calificacion(**cd))
            await db.flush()
            print(f"  Creadas {len(calificaciones_data)} calificaciones")
        else:
            print(f"  Ya existen {count} calificaciones, se saltan")

        await db.commit()

        # --- Summary ---
        print("\n✅ Seed data creada exitosamente:\n")
        for codigo, _ in carreras_data:
            print(f"  Carrera: {codigo}")
        for codigo, nombre, _ in materias_data:
            print(f"  Materia: {codigo} - {nombre}")
        print(f"  Cohorte: 2026")
        print(f"  Alumnos: {len(alumnos)}")
        for codigo in materias:
            print(f"  Entradas Padrón ({codigo}): {len(entrada_ids.get(codigo, []))}")
        print(f"  Asignaciones: {len(asignaciones)} (admin como profesor)")
        print(f"  Umbral: PROG1 configurado")
        print()


if __name__ == "__main__":
    asyncio.run(seed())
