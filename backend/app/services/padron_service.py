import csv
import io
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.core.security import encrypt
from app.integrations.moodle_ws import MoodleClient
from app.models.entrada_padron import EntradaPadron
from app.repositories.padron_repository import (
    EntradaPadronRepository,
    VersionPadronRepository,
)
from app.services.audit_service import AuditLogService

COLUMNAS_REQUERIDAS = {"nombre", "apellidos", "email", "comision", "regional"}


class PadronService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._version_repo = VersionPadronRepository(tenant_id)
        self._entrada_repo = EntradaPadronRepository(tenant_id)
        self._audit_service = AuditLogService(tenant_id)

    @staticmethod
    def parse_file(content: bytes, filename: str) -> list[dict[str, Any]]:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext == "csv":
            return PadronService._parse_csv(content)
        elif ext == "xlsx":
            return PadronService._parse_xlsx(content)
        else:
            raise DomainError(
                "Formato de archivo no soportado. Use .csv o .xlsx"
            )

    @staticmethod
    def _parse_csv(content: bytes) -> list[dict[str, Any]]:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        if rows:
            cols = set(rows[0].keys())
            missing = COLUMNAS_REQUERIDAS - cols
            if missing:
                raise DomainError(
                    f"Columnas faltantes en el archivo: {', '.join(sorted(missing))}"
                )
        return rows

    @staticmethod
    def _parse_xlsx(content: bytes) -> list[dict[str, Any]]:
        import openpyxl

        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
        ws = wb.active
        if ws is None:
            wb.close()
            raise DomainError("El archivo xlsx no tiene hojas")

        rows_iter = ws.iter_rows(values_only=True)
        headers = [
            str(h).lower().strip() if h is not None else ""
            for h in next(rows_iter, [])
        ]
        cols = set(headers)
        missing = COLUMNAS_REQUERIDAS - cols
        if missing:
            wb.close()
            raise DomainError(
                f"Columnas faltantes en el archivo: {', '.join(sorted(missing))}"
            )

        result = []
        for row in rows_iter:
            if any(cell is not None for cell in row):
                result.append(
                    {
                        headers[i]: (str(row[i]) if row[i] is not None else "")
                        for i in range(len(headers))
                    }
                )
        wb.close()
        return result

    def preview(self, content: bytes, filename: str) -> dict[str, Any]:
        rows = self.parse_file(content, filename)
        columnas = list(rows[0].keys()) if rows else list(COLUMNAS_REQUERIDAS)
        return {
            "filas_detectadas": len(rows),
            "columnas": columnas,
            "preview": rows[:5],
        }

    async def confirm_import(
        self,
        db: AsyncSession,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        content: bytes,
        filename: str,
        usuario_id: uuid.UUID,
    ) -> dict[str, Any]:
        rows = self.parse_file(content, filename)

        version = await self._version_repo.create(
            db,
            {
                "materia_id": materia_id,
                "cohorte_id": cohorte_id,
                "cargado_por": usuario_id,
                "activa": False,
            },
        )

        entradas = [
            EntradaPadron(
                tenant_id=self._version_repo._tenant_id,
                version_id=version.id,
                nombre=row.get("nombre", ""),
                apellidos=row.get("apellidos", ""),
                email=encrypt(row.get("email", "")),
                comision=row.get("comision") or None,
                regional=row.get("regional") or None,
            )
            for row in rows
        ]

        await self._entrada_repo.bulk_create(db, entradas)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.PADRON_CARGAR,
            materia_id=materia_id,
            filas_afectadas=len(rows),
        )

        return {
            "version_id": str(version.id),
            "filas_creadas": len(rows),
            "mensaje": f"Se importaron {len(rows)} alumnos correctamente",
        }

    async def activate_version(
        self,
        db: AsyncSession,
        version_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> None:
        version = await self._version_repo.get(db, version_id)
        if version is None:
            raise DomainError(f"Version {version_id} no encontrada")

        await self._version_repo.deactivate_all(
            db, version.materia_id, version.cohorte_id
        )
        await self._version_repo.update(db, version_id, {"activa": True})

    async def vaciar_materia(
        self,
        db: AsyncSession,
        materia_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> None:
        await self._entrada_repo.soft_delete_by_materia(db, materia_id)
        await self._version_repo.soft_delete_by_materia(db, materia_id)

    async def sync_from_moodle(
        self,
        db: AsyncSession,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        moodle_course_id: int,
        moodle_url: str,
        ws_token: str,
        usuario_id: uuid.UUID,
    ) -> dict[str, Any]:
        client = MoodleClient(moodle_url, ws_token)
        moodle_users = await client.sync_users(moodle_course_id)

        rows = [
            {
                "nombre": u.get("firstname", ""),
                "apellidos": u.get("lastname", ""),
                "email": u.get("email", ""),
                "comision": "",
                "regional": "",
            }
            for u in moodle_users
        ]

        if not rows:
            return {
                "version_id": None,
                "filas_creadas": 0,
                "mensaje": "No se encontraron alumnos en Moodle",
            }

        csv_content = PadronService._rows_to_csv(rows)
        return await self.confirm_import(
            db,
            materia_id,
            cohorte_id,
            csv_content.encode(),
            "moodle_import.csv",
            usuario_id,
        )

    @staticmethod
    def _rows_to_csv(rows: list[dict]) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["nombre", "apellidos", "email", "comision", "regional"]
        )
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()
