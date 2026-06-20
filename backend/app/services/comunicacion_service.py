import uuid
from datetime import datetime, timezone
from string import Template

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError, EntityNotFoundError
from app.core.security import decrypt, encrypt
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.models.tenant import Tenant
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.repositories.padron_repository import (
    EntradaPadronRepository,
    VersionPadronRepository,
)
from app.services.audit_service import AuditLogService


class ComunicacionService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._comunicacion_repo = ComunicacionRepository(tenant_id)
        self._version_repo = VersionPadronRepository(tenant_id)
        self._entrada_repo = EntradaPadronRepository(tenant_id)
        self._audit_service = AuditLogService(tenant_id)
        self._tenant_id = tenant_id

    @staticmethod
    def _transiciones_validas() -> dict[str, set[str]]:
        return {
            EstadoComunicacion.NUEVA: {
                EstadoComunicacion.PENDIENTE,
                EstadoComunicacion.PENDIENTE_APROBACION,
            },
            EstadoComunicacion.PENDIENTE_APROBACION: {
                EstadoComunicacion.PENDIENTE,
                EstadoComunicacion.CANCELADO,
            },
            EstadoComunicacion.PENDIENTE: {
                EstadoComunicacion.ENVIANDO,
                EstadoComunicacion.CANCELADO,
            },
            EstadoComunicacion.ENVIANDO: {
                EstadoComunicacion.ENVIADO,
                EstadoComunicacion.PENDIENTE,
                EstadoComunicacion.ERROR,
            },
        }

    @staticmethod
    def _validar_transicion(estado_actual: str, estado_destino: str) -> None:
        transiciones = ComunicacionService._transiciones_validas()
        destinos_validos = transiciones.get(estado_actual, set())
        if estado_destino not in destinos_validos:
            raise DomainError(
                f"Transición inválida: {estado_actual} → {estado_destino}"
            )

    async def _get_tenant(self, db: AsyncSession) -> Tenant:
        tenant = await db.get(Tenant, self._tenant_id)
        if tenant is None:
            raise DomainError("Tenant no encontrado")
        return tenant

    async def _buscar_padron_activo(
        self, db: AsyncSession, materia_id: uuid.UUID
    ):
        versiones = await self._version_repo.get_active_by_materia(
            db, materia_id
        )
        if not versiones:
            raise DomainError(
                "No hay un padrón activo para esta materia"
            )
        return versiones[0]

    async def preview(
        self,
        materia_id: uuid.UUID,
        destinatario_email: str,
        asunto_template: str,
        cuerpo_template: str,
        db: AsyncSession,
    ) -> dict[str, str]:
        version = await self._buscar_padron_activo(db, materia_id)
        entradas = await self._entrada_repo.get_by_version(db, version.id)

        entrada = None
        for e in entradas:
            if e.email.strip().lower() == destinatario_email.strip().lower():
                entrada = e
                break

        if entrada is None:
            if not entradas:
                raise DomainError("No hay entradas en el padrón activo")
            raise DomainError("Destinatario no encontrado")

        variables = {
            "nombre": entrada.nombre,
            "apellidos": entrada.apellidos,
            "materia": "",  
            "comision": entrada.comision or "",
        }

        asunto = Template(asunto_template).safe_substitute(variables)
        cuerpo = Template(cuerpo_template).safe_substitute(variables)

        return {"asunto": asunto, "cuerpo": cuerpo}

    async def enviar(
        self,
        materia_id: uuid.UUID,
        destinatarios: list[str],
        asunto_template: str,
        cuerpo_template: str,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict[str, str | int]:
        tenant = await self._get_tenant(db)
        lote_id = uuid.uuid4()
        requiere_aprobacion = tenant.requiere_aprobacion_comunicaciones

        if requiere_aprobacion:
            estado_inicial = EstadoComunicacion.PENDIENTE_APROBACION
        else:
            estado_inicial = EstadoComunicacion.PENDIENTE

        now = datetime.now(timezone.utc)
        for email in destinatarios:
            destinatario_cifrado = encrypt(email.strip().lower())
            data = {
                "enviado_por": usuario_id,
                "materia_id": materia_id,
                "destinatario": destinatario_cifrado,
                "asunto": asunto_template,
                "cuerpo": cuerpo_template,
                "lote_id": lote_id,
                "estado": estado_inicial,
                "enqueue_at": now,
            }
            await self._comunicacion_repo.create(db, data)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.COMUNICACION_ENVIAR,
            materia_id=materia_id,
            filas_afectadas=len(destinatarios),
            detalle={
                "lote_id": str(lote_id),
                "cantidad": len(destinatarios),
                "requiere_aprobacion": requiere_aprobacion,
            },
        )

        return {
            "lote_id": str(lote_id),
            "cantidad": len(destinatarios),
            "estado": estado_inicial,
        }

    async def aprobar_lote(
        self,
        lote_id: uuid.UUID,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        filas = await self._comunicacion_repo.batch_update_estado(
            db,
            lote_id,
            EstadoComunicacion.PENDIENTE_APROBACION,
            EstadoComunicacion.PENDIENTE,
        )

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.COMUNICACION_ENVIAR,
            filas_afectadas=filas,
            detalle={
                "lote_id": str(lote_id),
                "aprobado": True,
                "cantidad": filas,
            },
        )

        return {"lote_id": str(lote_id), "aprobadas": filas}

    async def rechazar_lote(
        self,
        lote_id: uuid.UUID,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        filas = await self._comunicacion_repo.batch_update_estado(
            db,
            lote_id,
            EstadoComunicacion.PENDIENTE_APROBACION,
            EstadoComunicacion.CANCELADO,
        )

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.COMUNICACION_ENVIAR,
            filas_afectadas=filas,
            detalle={
                "lote_id": str(lote_id),
                "aprobado": False,
                "cantidad": filas,
            },
        )

        return {"lote_id": str(lote_id), "rechazadas": filas}

    async def aprobar_comunicacion(
        self,
        comunicacion_id: uuid.UUID,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        comunicacion = await self._comunicacion_repo.get(db, comunicacion_id)
        if comunicacion is None:
            raise EntityNotFoundError("Comunicacion", comunicacion_id)

        self._validar_transicion(
            comunicacion.estado, EstadoComunicacion.PENDIENTE
        )

        comunicacion.estado = EstadoComunicacion.PENDIENTE
        await db.flush()
        await db.refresh(comunicacion)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.COMUNICACION_ENVIAR,
            filas_afectadas=1,
            detalle={
                "comunicacion_id": str(comunicacion_id),
                "aprobado": True,
            },
        )

        return {"comunicacion_id": str(comunicacion_id), "estado": EstadoComunicacion.PENDIENTE}

    async def cancelar(
        self,
        comunicacion_id: uuid.UUID,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        comunicacion = await self._comunicacion_repo.get(db, comunicacion_id)
        if comunicacion is None:
            raise EntityNotFoundError("Comunicacion", comunicacion_id)

        self._validar_transicion(
            comunicacion.estado, EstadoComunicacion.CANCELADO
        )

        comunicacion.estado = EstadoComunicacion.CANCELADO
        await db.flush()
        await db.refresh(comunicacion)

        return {"comunicacion_id": str(comunicacion_id), "estado": EstadoComunicacion.CANCELADO}

    async def listar(
        self,
        db: AsyncSession,
        *,
        lote_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        estado: str | None = None,
        pagina: int = 1,
        por_pagina: int = 50,
    ) -> dict[str, list | int]:
        comunicaciones = await self._comunicacion_repo.get_all(
            db, **{k: v for k, v in {"lote_id": lote_id, "materia_id": materia_id, "estado": estado}.items() if v is not None}
        )

        total = len(comunicaciones)
        offset = (pagina - 1) * por_pagina
        pagina_items = comunicaciones[offset : offset + por_pagina]

        items = []
        for c in pagina_items:
            d = self._serializar(c)
            items.append(d)

        return {"items": items, "total": total, "pagina": pagina, "por_pagina": por_pagina}

    async def obtener(
        self,
        comunicacion_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict | None:
        comunicacion = await self._comunicacion_repo.get(db, comunicacion_id)
        if comunicacion is None:
            return None
        return self._serializar(comunicacion)

    async def listar_lotes(
        self,
        db: AsyncSession,
    ) -> list[dict]:
        comunicaciones = await self._comunicacion_repo.get_all(db)
        lotes: dict[str, dict] = {}
        for c in comunicaciones:
            if c.lote_id is None:
                continue
            lid = str(c.lote_id)
            if lid not in lotes:
                lotes[lid] = {
                    "lote_id": lid,
                    "total": 0,
                    "conteo_por_estado": {},
                    "primer_envio": None,
                    "ultimo_envio": None,
                }
            lotes[lid]["total"] += 1
            lotes[lid]["conteo_por_estado"][c.estado] = (
                lotes[lid]["conteo_por_estado"].get(c.estado, 0) + 1
            )
            if c.enqueue_at is not None:
                ts = c.enqueue_at.isoformat()
                if lotes[lid]["primer_envio"] is None or ts < lotes[lid]["primer_envio"]:
                    lotes[lid]["primer_envio"] = ts
                if lotes[lid]["ultimo_envio"] is None or ts > lotes[lid]["ultimo_envio"]:
                    lotes[lid]["ultimo_envio"] = ts

        return list(lotes.values())

    async def procesar_cola(
        self,
        db: AsyncSession,
        proveedor_envio,
    ) -> dict[str, int]:
        pendientes = await ComunicacionRepository.get_all_pendientes_cross_tenant(db, limit=50)
        procesadas = 0
        exitos = 0
        errores = 0
        reintentos = 0

        for comunicacion in pendientes:
            try:
                self._validar_transicion(
                    comunicacion.estado, EstadoComunicacion.ENVIANDO
                )
            except DomainError:
                continue

            comunicacion.estado = EstadoComunicacion.ENVIANDO
            await db.flush()

            try:
                await proveedor_envio.enviar(
                    destinatario=decrypt(comunicacion.destinatario),
                    asunto=comunicacion.asunto,
                    cuerpo=comunicacion.cuerpo,
                )
                comunicacion.estado = EstadoComunicacion.ENVIADO
                comunicacion.enviado_at = datetime.now(timezone.utc)
                comunicacion.intentos += 1
                exitos += 1

                await self._audit_service.log(
                    db,
                    actor_id=comunicacion.enviado_por,
                    accion=AuditLogService.COMUNICACION_ENVIAR,
                    materia_id=comunicacion.materia_id,
                    filas_afectadas=1,
                    detalle={
                        "lote_id": str(comunicacion.lote_id),
                        "comunicacion_id": str(comunicacion.id),
                        "evento": "enviado",
                    },
                )
            except Exception as exc:
                comunicacion.intentos += 1
                if comunicacion.intentos >= 3:
                    comunicacion.estado = EstadoComunicacion.ERROR
                    comunicacion.error_msg = str(exc)
                    errores += 1

                    await self._audit_service.log(
                        db,
                        actor_id=comunicacion.enviado_por,
                        accion=AuditLogService.COMUNICACION_ENVIAR,
                        materia_id=comunicacion.materia_id,
                        filas_afectadas=1,
                        detalle={
                            "lote_id": str(comunicacion.lote_id),
                            "comunicacion_id": str(comunicacion.id),
                            "evento": "error",
                            "intentos": comunicacion.intentos,
                            "error": str(exc),
                        },
                    )
                else:
                    comunicacion.estado = EstadoComunicacion.PENDIENTE
                    reintentos += 1

            await db.flush()
            procesadas += 1

        await db.commit()
        return {
            "procesadas": procesadas,
            "exitos": exitos,
            "reintentos": reintentos,
            "errores": errores,
        }

    @staticmethod
    def _serializar(comunicacion: Comunicacion) -> dict:
        destinatario = comunicacion.destinatario
        try:
            from app.core.security import is_encrypted
            if is_encrypted(destinatario):
                destinatario = decrypt(destinatario)
        except Exception:
            pass

        return {
            "id": str(comunicacion.id),
            "tenant_id": str(comunicacion.tenant_id),
            "enviado_por": str(comunicacion.enviado_por),
            "materia_id": str(comunicacion.materia_id),
            "destinatario": destinatario,
            "asunto": comunicacion.asunto,
            "cuerpo": comunicacion.cuerpo,
            "lote_id": str(comunicacion.lote_id) if comunicacion.lote_id else None,
            "intentos": comunicacion.intentos,
            "error_msg": comunicacion.error_msg,
            "estado": comunicacion.estado,
            "enviado_at": comunicacion.enviado_at.isoformat() if comunicacion.enviado_at else None,
            "enqueue_at": comunicacion.enqueue_at.isoformat() if comunicacion.enqueue_at else None,
            "created_at": comunicacion.created_at.isoformat() if comunicacion.created_at else None,
        }
