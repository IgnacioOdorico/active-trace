"""Carreras, materias, cohortes, padrón, asignaciones, umbral y calificaciones."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.umbral_materia import UmbralMateria
from app.models.user import User
from app.models.version_padron import VersionPadron


async def seed_academico(
    db: AsyncSession,
    admin: User,
    tenant_id: uuid.UUID,
    now: datetime,
) -> dict[str, Any]:
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

    carreras = {}
    for codigo, _ in carreras_data:
        result = await db.execute(
            select(Carrera).where(
                Carrera.tenant_id == tenant_id,
                Carrera.codigo == codigo,
                Carrera.deleted_at.is_(None),
            )
        )
        carreras[codigo] = result.unique().scalar_one()

    materias_data = [
        ("PROG1", "Programación I", carreras["TUP"].id),
        ("PROG2", "Programación II", carreras["TUP"].id),
        ("BD1", "Base de Datos I", carreras["TUP"].id),
        ("MAT1", "Matemática I", carreras["TUP"].id),
        ("ING1", "Inglés I", carreras["TUP"].id),
    ]
    # Clave de categoría de Plus salarial (RN-33/PA-22), fija/precargada por
    # producto. Agrupa materias afines (PROG1+PROG2 -> "PROG") para el
    # cálculo de liquidaciones; ver alembic/versions/017_materia_clave_plus.py.
    clave_plus_por_codigo = {
        "PROG1": "PROG",
        "PROG2": "PROG",
        "BD1": "BD",
        "MAT1": "MAT",
        "ING1": "ING",
    }
    for codigo, nombre, carrera_id in materias_data:
        existing = await db.execute(
            select(Materia).where(
                Materia.tenant_id == tenant_id,
                Materia.codigo == codigo,
                Materia.deleted_at.is_(None),
            )
        )
        materia_existente = existing.unique().scalar_one_or_none()
        if materia_existente is None:
            db.add(Materia(
                tenant_id=tenant_id,
                codigo=codigo,
                nombre=nombre,
                carrera_id=carrera_id,
                clave_plus=clave_plus_por_codigo.get(codigo),
            ))
        elif materia_existente.clave_plus is None:
            materia_existente.clave_plus = clave_plus_por_codigo.get(codigo)
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
        materias[codigo] = result.unique().scalar_one()

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

    # Cantidad de inscriptos por materia (distinta a propósito, para
    # poder distinguir visualmente el padrón de cada materia en /reportes).
    inscriptos_por_materia: dict[str, int] = {
        "PROG1": 12,
        "BD1": 9,
        "PROG2": 7,
        "MAT1": 5,
        "ING1": 3,
    }

    entrada_ids: dict[str, list[uuid.UUID]] = {codigo: [] for codigo in materias}

    for idx, (nombre, apellidos, email, comision, regional) in enumerate(alumnos):
        for codigo, version in versiones.items():
            if idx >= inscriptos_por_materia.get(codigo, len(alumnos)):
                continue
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
            db.add(Asignacion(
                tenant_id=tenant_id,
                usuario_id=admin.id,
                rol="PROFESOR",
                materia_id=materia.id,
                carrera_id=materia.carrera_id,
                cohorte_id=cohorte.id,
                comisiones=["A", "B"],
                desde=datetime(2026, 1, 1, tzinfo=timezone.utc),
                hasta=datetime(2026, 12, 31, tzinfo=timezone.utc),
            ))
    await db.flush()

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

    if "PROG1" in asignaciones:
        existing_umbral = await db.execute(
            select(UmbralMateria).where(
                UmbralMateria.tenant_id == tenant_id,
                UmbralMateria.asignacion_id == asignaciones["PROG1"],
                UmbralMateria.deleted_at.is_(None),
            )
        )
        if existing_umbral.unique().scalar_one_or_none() is None:
            db.add(UmbralMateria(
                tenant_id=tenant_id,
                asignacion_id=asignaciones["PROG1"],
                materia_id=materias["PROG1"].id,
                umbral_pct=60.0,
                valores_aprobatorios=["Aprobado", "APROBADO", "8", "9", "10"],
            ))
    await db.flush()

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

        for eid in entrada_ids.get("PROG1", []):
            for i, act in enumerate(actividades):
                nota = 40 + (i * 10) + (hash(str(eid)) % 20)
                nota_num = max(1, min(100, nota))
                calificaciones_data.append({
                    "tenant_id": tenant_id,
                    "entrada_padron_id": eid,
                    "materia_id": materias["PROG1"].id,
                    "nombre_actividad": act,
                    "nota_numerica": float(nota_num),
                    "nota_textual": None,
                    "aprobado": nota_num >= 60,
                    "origen": "Seed",
                    "importado_at": now,
                })

        for eid in entrada_ids.get("BD1", [])[:8]:
            for i, act in enumerate(actividades[:3]):
                nota = 45 + (i * 8) + (hash(str(eid)) % 25)
                nota_num = max(1, min(100, nota))
                calificaciones_data.append({
                    "tenant_id": tenant_id,
                    "entrada_padron_id": eid,
                    "materia_id": materias["BD1"].id,
                    "nombre_actividad": act,
                    "nota_numerica": float(nota_num),
                    "nota_textual": None,
                    "aprobado": nota_num >= 60,
                    "origen": "Seed",
                    "importado_at": now,
                })

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

    return {
        "carreras": carreras,
        "carreras_data": carreras_data,
        "materias": materias,
        "materias_data": materias_data,
        "cohorte": cohorte,
        "versiones": versiones,
        "alumnos": alumnos,
        "entrada_ids": entrada_ids,
        "asignaciones": asignaciones,
    }
