import uuid
from io import BytesIO

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.asignacion import Asignacion
from app.models.user import User, nombre_completo_usuario
from app.repositories.asignacion import AsignacionRepository
from app.schemas.equipos import (
    AsignacionMasivaRequest,
    ClonarRequest,
    VigenciaRequest,
)
from app.services.audit_service import AuditLogService, ASIGNACION_MODIFICAR

ROLES_ASIGNABLES_EQUIPO = ("PROFESOR", "TUTOR", "NEXO")


class EquipoService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._tenant_id = tenant_id
        self._repo = AsignacionRepository(tenant_id)
        self._audit = AuditLogService(tenant_id)

    async def listar_docentes_disponibles(self, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            select(User).where(
                User.tenant_id == self._tenant_id,
                User.deleted_at.is_(None),
                User.is_active.is_(True),
            )
        )
        usuarios = result.unique().scalars().all()

        docentes = []
        for u in usuarios:
            roles_usuario = sorted(
                {r.codigo for r in u.roles} & set(ROLES_ASIGNABLES_EQUIPO)
            )
            if roles_usuario:
                docentes.append({
                    "id": u.id,
                    "nombre_completo": nombre_completo_usuario(u.nombre, u.apellidos, u.email),
                    "email": u.email,
                    "roles": roles_usuario,
                })
        return docentes

    async def listar_mis_equipos(
        self,
        db: AsyncSession,
        usuario_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        rol: str | None = None,
        estado_vigencia: str | None = None,
    ) -> list[Asignacion]:
        filters: dict = {"usuario_id": usuario_id}
        if materia_id is not None:
            filters["materia_id"] = materia_id
        if rol is not None:
            filters["rol"] = rol

        asignaciones = list(await self._repo.get_all(db, **filters))

        if estado_vigencia is not None:
            asignaciones = [
                a for a in asignaciones if a.estado_vigencia == estado_vigencia
            ]

        return asignaciones

    async def asignacion_masiva(
        self,
        db: AsyncSession,
        request: AsignacionMasivaRequest,
        usuario_actual_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        ids_creados: list[uuid.UUID] = []
        for usuario_id in request.usuario_ids:
            data = {
                "usuario_id": usuario_id,
                "rol": request.rol,
                "materia_id": request.materia_id,
                "carrera_id": request.carrera_id,
                "cohorte_id": request.cohorte_id,
                "comisiones": request.comisiones,
                "desde": request.desde,
                "hasta": request.hasta,
            }
            asignacion = await self._repo.create(db, data)
            ids_creados.append(asignacion.id)

        await self._audit.log(
            db,
            actor_id=usuario_actual_id,
            accion=ASIGNACION_MODIFICAR,
            materia_id=request.materia_id,
            detalle={
                "tipo": "asignacion_masiva",
                "cantidad": len(request.usuario_ids),
            },
            filas_afectadas=len(request.usuario_ids),
        )

        return ids_creados

    async def clonar_equipo(
        self,
        db: AsyncSession,
        request: ClonarRequest,
        usuario_actual_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        query = (
            select(Asignacion)
            .where(
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.materia_id == request.materia_id,
                Asignacion.cohorte_id == request.cohorte_origen_id,
            )
            .with_for_update()
        )
        result = await db.execute(query)
        source_asignaciones = list(result.unique().scalars().all())

        if not source_asignaciones:
            return []

        ids_creados: list[uuid.UUID] = []
        for src in source_asignaciones:
            data = {
                "usuario_id": src.usuario_id,
                "rol": src.rol,
                "materia_id": request.materia_id,
                "carrera_id": src.carrera_id,
                "cohorte_id": request.cohorte_destino_id,
                "comisiones": src.comisiones,
                "responsable_id": src.responsable_id,
                "desde": request.desde,
                "hasta": request.hasta,
            }
            new_asignacion = await self._repo.create(db, data)
            ids_creados.append(new_asignacion.id)

        await self._audit.log(
            db,
            actor_id=usuario_actual_id,
            accion=ASIGNACION_MODIFICAR,
            materia_id=request.materia_id,
            detalle={
                "tipo": "clonar_equipo",
                "cohorte_origen": str(request.cohorte_origen_id),
                "cohorte_destino": str(request.cohorte_destino_id),
            },
            filas_afectadas=len(source_asignaciones),
        )

        return ids_creados

    async def modificar_vigencia(
        self,
        db: AsyncSession,
        asignacion_id: uuid.UUID,
        request: VigenciaRequest,
        usuario_actual_id: uuid.UUID,
    ) -> Asignacion:
        update_data: dict = {}
        if request.desde is not None:
            update_data["desde"] = request.desde
        if request.hasta is not None:
            update_data["hasta"] = request.hasta

        asignacion = await self._repo.update(db, asignacion_id, update_data)

        await self._audit.log(
            db,
            actor_id=usuario_actual_id,
            accion=ASIGNACION_MODIFICAR,
            detalle={
                "tipo": "modificar_vigencia",
                "asignacion_id": str(asignacion_id),
            },
            filas_afectadas=1,
        )

        return asignacion

    async def modificar_vigencia_masiva(
        self,
        db: AsyncSession,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        request: VigenciaRequest,
        usuario_actual_id: uuid.UUID,
    ) -> int:
        update_data: dict = {}
        if request.desde is not None:
            update_data["desde"] = request.desde
        if request.hasta is not None:
            update_data["hasta"] = request.hasta

        if not update_data:
            return 0

        stmt = (
            update(Asignacion)
            .where(
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.materia_id == materia_id,
                Asignacion.cohorte_id == cohorte_id,
            )
            .values(**update_data)
        )
        result = await db.execute(stmt)
        filas_afectadas = result.rowcount

        await self._audit.log(
            db,
            actor_id=usuario_actual_id,
            accion=ASIGNACION_MODIFICAR,
            materia_id=materia_id,
            detalle={
                "tipo": "modificar_vigencia_masiva",
                "cohorte_id": str(cohorte_id),
            },
            filas_afectadas=filas_afectadas,
        )

        return filas_afectadas

    async def exportar_equipo(
        self,
        db: AsyncSession,
        asignacion_id: uuid.UUID,
    ) -> bytes:
        asignacion = await self._repo.get(db, asignacion_id)
        if asignacion is None:
            raise EntityNotFoundError(
                entity_type="Asignacion", entity_id=asignacion_id
            )

        filters: dict = {}
        if asignacion.materia_id is not None:
            filters["materia_id"] = asignacion.materia_id
        if asignacion.cohorte_id is not None:
            filters["cohorte_id"] = asignacion.cohorte_id

        equipo = list(await self._repo.get_all(db, **filters))

        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Equipo Docente"

        ws.append(["Usuario ID", "Rol", "Materia ID", "Comisiones", "Desde", "Hasta", "Estado"])

        for a in equipo:
            ws.append([
                str(a.usuario_id),
                a.rol,
                str(a.materia_id) if a.materia_id else "",
                ", ".join(a.comisiones) if a.comisiones else "",
                a.desde.isoformat() if a.desde else "",
                a.hasta.isoformat() if a.hasta else "",
                a.estado_vigencia,
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
