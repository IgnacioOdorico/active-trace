import uuid
from datetime import date, timedelta
from string import Template

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.repositories.instancia_encuentro_repository import InstanciaEncuentroRepository
from app.repositories.slot_encuentro_repository import SlotEncuentroRepository
from app.services.audit_service import AuditLogService


_DIAS_SEMANA = {
    "Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3,
    "Viernes": 4, "Sábado": 5, "Domingo": 6,
}

_TRANSICIONES_ENCUENTRO: dict[str, set[str]] = {
    "Programado": {"Programado", "Realizado", "Cancelado"},
    "Realizado": {"Realizado"},
    "Cancelado": {"Cancelado"},
}

_HTML_TEMPLATE = Template("""<table class="encuentros">
<thead><tr><th>Fecha</th><th>Hora</th><th>Título</th><th>Enlace</th><th>Estado</th><th>Grabación</th></tr></thead>
<tbody>
$filas
</tbody>
</table>""")

_HTML_SIN_ENCUENTROS = '<p>No hay encuentros programados</p>'

_HTML_FILA = Template(
    "<tr><td>$fecha</td><td>$hora</td><td>$titulo</td>"
    "<td><a href=\"$meet_url\">Link</a></td>"
    "<td>$estado</td><td>$video_link</td></tr>"
)


class EncuentroService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._slot_repo = SlotEncuentroRepository(tenant_id)
        self._instancia_repo = InstanciaEncuentroRepository(tenant_id)
        self._audit_service = AuditLogService(tenant_id)

    @staticmethod
    def _calcular_fechas(
        fecha_inicio: date, dia_semana: str, cant_semanas: int
    ) -> list[date]:
        if cant_semanas > 52:
            raise DomainError(
                "cant_semanas máximo es 52"
            )

        dia_num = _DIAS_SEMANA.get(dia_semana)
        if dia_num is None:
            raise DomainError(f"dia_semana inválido: {dia_semana}")

        if fecha_inicio.weekday() != dia_num:
            raise DomainError(
                f"fecha_inicio ({fecha_inicio}) no coincide con dia_semana ({dia_semana})"
            )

        return [fecha_inicio + timedelta(weeks=i) for i in range(cant_semanas)]

    @staticmethod
    def _validar_transicion_estado(actual: str, destino: str) -> None:
        if destino not in _TRANSICIONES_ENCUENTRO.get(actual, set()):
            raise DomainError(
                f"Transición inválida: {actual} → {destino}"
            )

    async def crear_slot_recurrente(
        self,
        data: dict,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        materia_id = uuid.UUID(str(data["materia_id"]))
        fechas = self._calcular_fechas(
            fecha_inicio=data["fecha_inicio"],
            dia_semana=data["dia_semana"],
            cant_semanas=data["cant_semanas"],
        )

        slot_data = {
            "asignacion_id": usuario_id,
            "materia_id": materia_id,
            "titulo": data["titulo"],
            "hora": data["hora"],
            "dia_semana": data["dia_semana"],
            "fecha_inicio": data["fecha_inicio"],
            "cant_semanas": data["cant_semanas"],
            "fecha_unica": data.get("fecha_unica"),
            "meet_url": data["meet_url"],
            "vig_desde": data["vig_desde"],
            "vig_hasta": data.get("vig_hasta"),
        }
        slot = await self._slot_repo.create(db, slot_data)

        for fecha in fechas:
            instancia_data = {
                "slot_id": slot.id,
                "materia_id": materia_id,
                "fecha": fecha,
                "hora": data["hora"],
                "titulo": data["titulo"],
                "meet_url": data["meet_url"],
            }
            await self._instancia_repo.create(db, instancia_data)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.ENCUENTRO_CREAR,
            materia_id=materia_id,
            detalle={
                "slot_id": str(slot.id),
                "cantidad_instancias": len(fechas),
            },
        )

        return {"id": str(slot.id), "instancias_generadas": len(fechas)}

    async def crear_encuentro_unico(
        self,
        data: dict,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        materia_id = uuid.UUID(str(data["materia_id"]))
        instancia_data = {
            "materia_id": materia_id,
            "fecha": data["fecha"],
            "hora": data["hora"],
            "titulo": data["titulo"],
            "meet_url": data.get("meet_url", ""),
            "video_url": data.get("video_url"),
            "comentario": data.get("comentario"),
        }
        instancia = await self._instancia_repo.create(db, instancia_data)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.ENCUENTRO_CREAR,
            materia_id=materia_id,
            detalle={
                "instancia_id": str(instancia.id),
            },
        )

        return {"id": str(instancia.id)}

    async def editar_instancia(
        self,
        instancia_id: uuid.UUID,
        data: dict,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        instancia = await self._instancia_repo.get(db, instancia_id)
        if instancia is None:
            raise DomainError(f"InstanciaEncuentro no encontrada: {instancia_id}")

        estado_anterior = instancia.estado
        if data.get("estado") is not None:
            self._validar_transicion_estado(estado_anterior, data["estado"])
            instancia.estado = data["estado"]
        if data.get("meet_url") is not None:
            instancia.meet_url = data["meet_url"]
        if data.get("video_url") is not None:
            instancia.video_url = data["video_url"]
        if data.get("comentario") is not None:
            instancia.comentario = data["comentario"]

        await db.flush()
        await db.refresh(instancia)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.ENCUENTRO_EDITAR,
            materia_id=instancia.materia_id,
            detalle={
                "instancia_id": str(instancia.id),
                "estado_anterior": estado_anterior,
                "estado_nuevo": instancia.estado,
            },
        )

        return {"id": str(instancia.id), "estado": instancia.estado}

    async def generar_html(
        self,
        materia_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        instancias = await self._instancia_repo.get_by_materia_filtros(
            db, materia_id=materia_id
        )

        if not instancias:
            return {"html": _HTML_SIN_ENCUENTROS}

        filas = []
        for inst in instancias:
            video = (
                f'<a href="{inst.video_url}">Ver grabación</a>'
                if inst.video_url else ""
            )
            filas.append(_HTML_FILA.substitute(
                fecha=inst.fecha.isoformat(),
                hora=inst.hora.isoformat()[:5],
                titulo=inst.titulo,
                meet_url=inst.meet_url,
                estado=inst.estado,
                video_link=video,
            ))

        html = _HTML_TEMPLATE.substitute(filas="\n".join(filas))
        return {"html": html}

    async def listar(
        self,
        filtros: dict,
        *,
        pagina: int = 1,
        page_size: int = 50,
        db: AsyncSession,
    ) -> dict:
        page_size = min(page_size, 100)
        materia_id = filtros.get("materia_id")
        if materia_id is not None:
            materia_id = uuid.UUID(str(materia_id))

        todas = await self._instancia_repo.get_by_materia_filtros(
            db,
            materia_id=materia_id,
            fecha_desde=filtros.get("fecha_desde"),
            fecha_hasta=filtros.get("fecha_hasta"),
            estado=filtros.get("estado"),
        )

        total = len(todas)
        offset = (pagina - 1) * page_size
        pagina_items = todas[offset : offset + page_size]

        items = []
        for inst in pagina_items:
            items.append({
                "id": str(inst.id),
                "slot_id": str(inst.slot_id) if inst.slot_id else None,
                "materia_id": str(inst.materia_id),
                "fecha": inst.fecha.isoformat(),
                "hora": inst.hora.isoformat()[:5],
                "titulo": inst.titulo,
                "estado": inst.estado,
                "meet_url": inst.meet_url,
                "video_url": inst.video_url,
                "comentario": inst.comentario,
            })

        return {
            "items": items,
            "total": total,
            "pagina": pagina,
            "page_size": page_size,
        }
