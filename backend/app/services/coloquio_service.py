import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.models.evaluacion import Evaluacion
from app.models.evaluacion_alumno import EvaluacionAlumno
from app.models.evaluacion_dia import EvaluacionDia
from app.models.reserva_evaluacion import EstadoReserva, ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.user import User
from app.repositories.evaluacion_alumno_repository import EvaluacionAlumnoRepository
from app.repositories.evaluacion_dia_repository import EvaluacionDiaRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.reserva_evaluacion_repository import ReservaEvaluacionRepository
from app.repositories.resultado_evaluacion_repository import ResultadoEvaluacionRepository
from app.services.audit_service import AuditLogService


class ColoquioService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._evaluacion_repo = EvaluacionRepository(tenant_id)
        self._evaluacion_dia_repo = EvaluacionDiaRepository(tenant_id)
        self._reserva_repo = ReservaEvaluacionRepository(tenant_id)
        self._resultado_repo = ResultadoEvaluacionRepository(tenant_id)
        self._alumno_repo = EvaluacionAlumnoRepository(tenant_id)
        self._audit_service = AuditLogService(tenant_id)

    async def crear_convocatoria(
        self, data: dict, usuario_id: uuid.UUID, db: AsyncSession
    ) -> dict:
        evaluacion_data = {
            "materia_id": uuid.UUID(str(data["materia_id"])),
            "cohorte_id": uuid.UUID(str(data["cohorte_id"])),
            "tipo": data["tipo"],
            "instancia": data["instancia"],
            "dias_disponibles": data["dias_disponibles"],
        }
        evaluacion = await self._evaluacion_repo.create(db, evaluacion_data)

        cupo_por_dia = data["cupo_por_dia"]
        today = date.today()
        for i in range(data["dias_disponibles"]):
            dia_data = {
                "evaluacion_id": evaluacion.id,
                "fecha": today + timedelta(days=i + 1),
                "cupo_maximo": cupo_por_dia,
                "cupos_restantes": cupo_por_dia,
            }
            await self._evaluacion_dia_repo.create(db, dia_data)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.COLOQUIO_CREAR,
            detalle={
                "evaluacion_id": str(evaluacion.id),
                "tipo": data["tipo"],
                "dias": data["dias_disponibles"],
                "cupo_por_dia": cupo_por_dia,
            },
        )

        return {
            "id": str(evaluacion.id),
            "materia_id": str(evaluacion.materia_id),
            "cohorte_id": str(evaluacion.cohorte_id),
            "tipo": evaluacion.tipo,
            "instancia": evaluacion.instancia,
            "dias_disponibles": evaluacion.dias_disponibles,
            "dias_generados": data["dias_disponibles"],
        }

    async def importar_alumnos(
        self, evaluacion_id: uuid.UUID, alumno_ids: list[str], db: AsyncSession
    ) -> int:
        evaluacion = await self._evaluacion_repo.get(db, evaluacion_id)
        if evaluacion is None:
            raise DomainError("Evaluación no encontrada", context={"evaluacion_id": str(evaluacion_id)})

        alumno_uuids = []
        for raw_id in alumno_ids:
            try:
                alumno_uuids.append(uuid.UUID(str(raw_id)))
            except ValueError:
                raise DomainError(f"ID de alumno inválido: {raw_id}")

        result = await db.execute(
            select(User.id).where(User.id.in_(alumno_uuids), User.deleted_at.is_(None))
        )
        existing_ids = set(result.scalars().all())
        missing = [str(uid) for uid in alumno_uuids if uid not in existing_ids]
        if missing:
            raise DomainError(
                f"Alumnos no encontrados: {', '.join(missing)}",
                context={"alumno_ids": missing},
            )

        return await self._alumno_repo.reemplazar_padron(evaluacion_id, alumno_uuids, db)

    async def reservar_turno(
        self,
        evaluacion_id: uuid.UUID,
        evaluacion_dia_id: uuid.UUID,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        evaluacion = await self._evaluacion_repo.get(db, evaluacion_id)
        if evaluacion is None:
            raise DomainError("Evaluación no encontrada")
        if evaluacion.estado == "Cerrada":
            raise DomainError("Convocatoria cerrada, no se permiten reservas")

        habilitados = await self._alumno_repo.get_alumnos_habilitados(evaluacion_id, db)
        habilitado_ids = {str(h.alumno_id) for h in habilitados}
        if str(usuario_id) not in habilitado_ids:
            raise DomainError("No está habilitado para esta convocatoria")

        dia = await self._evaluacion_dia_repo.get(db, evaluacion_dia_id)
        if dia is None or str(dia.evaluacion_id) != str(evaluacion_id):
            raise DomainError("Día no encontrado para esta evaluación")

        if dia.cupos_restantes <= 0:
            raise DomainError("Cupo agotado para el día seleccionado")

        ok = await self._evaluacion_dia_repo.decrementar_cupo(evaluacion_dia_id, db)
        if not ok:
            raise DomainError("Cupo agotado para el día seleccionado")

        reserva = await self._reserva_repo.create(
            db,
            {
                "evaluacion_dia_id": evaluacion_dia_id,
                "alumno_id": usuario_id,
            },
        )

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.COLOQUIO_RESERVAR,
            detalle={
                "reserva_id": str(reserva.id),
                "evaluacion_dia_id": str(evaluacion_dia_id),
                "evaluacion_id": str(evaluacion_id),
            },
        )

        return {
            "id": str(reserva.id),
            "evaluacion_dia_id": str(evaluacion_dia_id),
            "fecha_hora": reserva.fecha_hora.isoformat() if hasattr(reserva, "fecha_hora") else None,
            "estado": reserva.estado,
        }

    async def cancelar_reserva(
        self, reserva_id: uuid.UUID, usuario_id: uuid.UUID, db: AsyncSession
    ) -> dict:
        reserva = await self._reserva_repo.get(db, reserva_id)
        if reserva is None:
            raise DomainError("Reserva no encontrada")
        if str(reserva.alumno_id) != str(usuario_id):
            raise DomainError("No puedes cancelar una reserva de otro alumno")
        if reserva.estado == EstadoReserva.CANCELADA:
            raise DomainError("La reserva ya está cancelada")

        reserva.estado = EstadoReserva.CANCELADA
        await db.flush()

        await self._evaluacion_dia_repo.incrementar_cupo(reserva.evaluacion_dia_id, db)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.COLOQUIO_RESERVAR,
            detalle={
                "reserva_id": str(reserva.id),
                "accion": "cancelada",
            },
        )

        return {"id": str(reserva.id), "estado": reserva.estado}

    async def listar_mis_reservas(
        self, usuario_id: uuid.UUID, db: AsyncSession
    ) -> list[dict]:
        reservas = await self._reserva_repo.get_activas_por_alumno(usuario_id, db)
        if not reservas:
            return []

        items = []
        for r in reservas:
            dia = await self._evaluacion_dia_repo.get(db, r.evaluacion_dia_id)
            evaluacion_nombre = None
            evaluacion_instancia = None
            dia_fecha = None
            if dia is not None:
                dia_fecha = dia.fecha
                ev = await self._evaluacion_repo.get(db, dia.evaluacion_id)
                if ev is not None:
                    evaluacion_nombre = ev.tipo
                    evaluacion_instancia = ev.instancia

            items.append({
                "id": str(r.id),
                "evaluacion_dia_id": str(r.evaluacion_dia_id),
                "alumno_id": str(r.alumno_id),
                "fecha_hora": r.fecha_hora.isoformat() if hasattr(r, "fecha_hora") else None,
                "estado": r.estado,
                "evaluacion_materia": evaluacion_nombre,
                "evaluacion_instancia": evaluacion_instancia,
                "dia_fecha": dia_fecha.isoformat() if dia_fecha else None,
            })
        return items

    async def registrar_resultado(
        self,
        evaluacion_id: uuid.UUID,
        alumno_id: uuid.UUID,
        nota_final: str,
        db: AsyncSession,
    ) -> dict:
        evaluacion = await self._evaluacion_repo.get(db, evaluacion_id)
        if evaluacion is None:
            raise DomainError("Evaluación no encontrada")

        habilitados = await self._alumno_repo.get_alumnos_habilitados(evaluacion_id, db)
        habilitado_ids = {str(h.alumno_id) for h in habilitados}
        if str(alumno_id) not in habilitado_ids:
            raise DomainError("El alumno no está en el padrón de esta evaluación")

        resultado = await self._resultado_repo.upsert(
            evaluacion_id, alumno_id, nota_final, db
        )
        return {
            "id": str(resultado.id),
            "evaluacion_id": str(resultado.evaluacion_id),
            "alumno_id": str(resultado.alumno_id),
            "nota_final": resultado.nota_final,
        }

    async def listar_resultados(
        self, evaluacion_id: uuid.UUID, db: AsyncSession
    ) -> list[dict]:
        resultados = await self._resultado_repo.get_por_evaluacion(evaluacion_id, db)
        if not resultados:
            return []

        alumno_ids = [r.alumno_id for r in resultados]
        result = await db.execute(
            select(User.id, User.nombre, User.apellido).where(User.id.in_(alumno_ids))
        )
        user_map = {}
        for row in result.all():
            user_map[str(row.id)] = {"nombre": row.nombre, "apellido": row.apellido}

        items = []
        for r in resultados:
            info = user_map.get(str(r.alumno_id), {})
            items.append({
                "id": str(r.id),
                "evaluacion_id": str(r.evaluacion_id),
                "alumno_id": str(r.alumno_id),
                "nota_final": r.nota_final,
                "alumno_nombre": info.get("nombre"),
                "alumno_apellido": info.get("apellido"),
            })
        return items

    async def obtener_metricas_globales(
        self, db: AsyncSession
    ) -> dict:
        total_convocados = await db.execute(
            select(func.count(func.distinct(EvaluacionAlumno.alumno_id)))
            .join(Evaluacion, EvaluacionAlumno.evaluacion_id == Evaluacion.id)
            .where(
                Evaluacion.tenant_id == self._evaluacion_repo._tenant_id,
                Evaluacion.deleted_at.is_(None),
                EvaluacionAlumno.deleted_at.is_(None),
            )
        )
        total_convocados = total_convocados.scalar_one()

        total_instancias = await self._evaluacion_repo.count(db)
        if total_instancias is None:
            total_instancias = 0

        result = await db.execute(
            select(func.count())
            .select_from(ReservaEvaluacion)
            .where(
                ReservaEvaluacion.tenant_id == self._reserva_repo._tenant_id,
                ReservaEvaluacion.deleted_at.is_(None),
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
            )
        )
        total_reservas = result.scalar_one()

        result = await db.execute(
            select(func.count())
            .select_from(ResultadoEvaluacion)
            .where(
                ResultadoEvaluacion.tenant_id == self._resultado_repo._tenant_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            )
        )
        total_notas = result.scalar_one()

        return {
            "total_alumnos_convocados": total_convocados,
            "total_instancias_activas": total_instancias,
            "total_reservas_activas": total_reservas,
            "total_notas_registradas": total_notas,
        }

    async def obtener_metricas_convocatoria(
        self, evaluacion_id: uuid.UUID, db: AsyncSession
    ) -> dict:
        result = await db.execute(
            select(func.count())
            .select_from(EvaluacionAlumno)
            .where(
                EvaluacionAlumno.evaluacion_id == evaluacion_id,
                EvaluacionAlumno.deleted_at.is_(None),
            )
        )
        convocados = result.scalar_one()

        reservas_activas = await self._reserva_repo.contar_activas(evaluacion_id, db)

        result = await db.execute(
            select(func.coalesce(func.sum(EvaluacionDia.cupos_restantes), 0))
            .where(
                EvaluacionDia.evaluacion_id == evaluacion_id,
                EvaluacionDia.deleted_at.is_(None),
            )
        )
        cupos_libres = result.scalar_one()

        result = await db.execute(
            select(func.count())
            .select_from(ResultadoEvaluacion)
            .where(
                ResultadoEvaluacion.evaluacion_id == evaluacion_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            )
        )
        notas = result.scalar_one()

        return {
            "convocados": convocados,
            "reservas_activas": reservas_activas,
            "cupos_libres": cupos_libres,
            "notas_registradas": notas,
        }

    async def listar_convocatorias(
        self,
        filtros: dict,
        *,
        pagina: int = 1,
        page_size: int = 50,
        db: AsyncSession,
    ) -> dict:
        materia_id = filtros.get("materia_id")
        if materia_id is not None:
            materia_id = uuid.UUID(str(materia_id))

        items, total = await self._evaluacion_repo.list_all_con_metricas(
            db, materia_id=materia_id, pagina=pagina, page_size=page_size
        )

        result_items = []
        for ev in items:
            metricas = await self.obtener_metricas_convocatoria(ev.id, db)
            result_items.append({
                "id": str(ev.id),
                "materia_id": str(ev.materia_id),
                "cohorte_id": str(ev.cohorte_id),
                "tipo": ev.tipo,
                "instancia": ev.instancia,
                "dias_disponibles": ev.dias_disponibles,
                "total_convocados": metricas["convocados"],
                "total_reservas_activas": metricas["reservas_activas"],
                "total_cupos_libres": metricas["cupos_libres"],
            })

        return {
            "items": result_items,
            "total": total,
            "pagina": pagina,
            "page_size": page_size,
        }

    async def obtener_agenda(
        self, evaluacion_id: uuid.UUID, db: AsyncSession
    ) -> list[dict]:
        reservas = await self._reserva_repo.get_activas_por_evaluacion(evaluacion_id, db)
        if not reservas:
            return []

        items = []
        for r in reservas:
            dia = await self._evaluacion_dia_repo.get(db, r.evaluacion_dia_id)
            user_result = await db.execute(
                select(User.nombre, User.apellido, User.email).where(User.id == r.alumno_id)
            )
            user_row = user_result.one_or_none()

            items.append({
                "reserva_id": str(r.id),
                "alumno_nombre": user_row.nombre if user_row else "",
                "alumno_apellido": user_row.apellido if user_row else "",
                "alumno_email": user_row.email if user_row else None,
                "fecha_reserva": dia.fecha.isoformat() if dia else None,
                "hora_reserva": r.fecha_hora.isoformat() if hasattr(r, "fecha_hora") else None,
            })

        items.sort(key=lambda x: x.get("fecha_reserva") or "")
        return items

    async def cerrar_convocatoria(
        self, evaluacion_id: uuid.UUID, usuario_id: uuid.UUID, db: AsyncSession
    ) -> dict:
        evaluacion = await self._evaluacion_repo.get(db, evaluacion_id)
        if evaluacion is None:
            raise DomainError("Evaluación no encontrada")
        if evaluacion.estado == "Cerrada":
            raise DomainError("La convocatoria ya está cerrada")

        evaluacion.estado = "Cerrada"
        await db.flush()
        await db.refresh(evaluacion)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.COLOQUIO_CERRAR,
            detalle={"evaluacion_id": str(evaluacion.id)},
        )

        return {"id": str(evaluacion.id), "estado": evaluacion.estado}

    async def editar_convocatoria(
        self, evaluacion_id: uuid.UUID, data: dict, db: AsyncSession
    ) -> dict:
        evaluacion = await self._evaluacion_repo.get(db, evaluacion_id)
        if evaluacion is None:
            raise DomainError("Evaluación no encontrada")
        if evaluacion.estado == "Cerrada":
            raise DomainError("No se puede editar una convocatoria cerrada")

        if "instancia" in data:
            evaluacion.instancia = data["instancia"]
        if "dias_disponibles" in data:
            evaluacion.dias_disponibles = data["dias_disponibles"]
        if "tipo" in data:
            evaluacion.tipo = data["tipo"]

        await db.flush()
        await db.refresh(evaluacion)

        return {
            "id": str(evaluacion.id),
            "materia_id": str(evaluacion.materia_id),
            "cohorte_id": str(evaluacion.cohorte_id),
            "tipo": evaluacion.tipo,
            "instancia": evaluacion.instancia,
            "dias_disponibles": evaluacion.dias_disponibles,
            "estado": evaluacion.estado,
        }

    async def listar_disponibles(
        self, usuario_id: uuid.UUID, db: AsyncSession
    ) -> list[dict]:
        habilitaciones = await self._alumno_repo.get_alumnos_habilitados_por_alumno(usuario_id, db)
        if not habilitaciones:
            return []

        items = []
        for hab in habilitaciones:
            ev = await self._evaluacion_repo.get(db, hab.evaluacion_id)
            if ev is None or ev.estado == "Cerrada":
                continue

            dias = await self._evaluacion_dia_repo.get_by_evaluacion(ev.id, db)
            dias_con_cupo = [d for d in dias if d.cupos_restantes > 0]
            if not dias_con_cupo:
                continue

            items.append({
                "id": str(ev.id),
                "materia_nombre": None,
                "instancia": ev.instancia,
                "tipo": ev.tipo,
                "dias_restantes_con_cupo": len(dias_con_cupo),
            })

        return items
