import csv
import io
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.padron_repository import (
    EntradaPadronRepository,
    VersionPadronRepository,
)
from app.repositories.umbral_repository import UmbralRepository
from app.services.audit_service import AuditLogService


class CalificacionParser:
    COLUMNAS_EMAIL = {"email", "dirección de correo"}
    COLUMNAS_NOMBRE = {"nombre"}
    COLUMNAS_APELLIDOS = {"apellido(s)", "apellidos", "apellido"}
    SUFIJO_NUMERICO = "(real)"

    @classmethod
    def _detect_column_types(
        cls, headers: list[str]
    ) -> tuple[list[str], list[str]]:
        numeric = []
        textual = []
        for h in headers:
            if cls.SUFIJO_NUMERICO in h.lower():
                numeric.append(h)
            else:
                textual.append(h)
        return numeric, textual

    @classmethod
    def _identify_student_column(
        cls, headers: list[str]
    ) -> tuple[str, str] | None:
        headers_lower = [h.lower().strip() for h in headers]

        for i, hl in enumerate(headers_lower):
            if hl in cls.COLUMNAS_EMAIL:
                return "email", headers[i]

        nombre_idx = None
        apellidos_idx = None
        for i, hl in enumerate(headers_lower):
            if hl in cls.COLUMNAS_NOMBRE:
                nombre_idx = i
            if hl in cls.COLUMNAS_APELLIDOS:
                apellidos_idx = i
        if nombre_idx is not None and apellidos_idx is not None:
            return "nombre_apellidos", (headers[nombre_idx], headers[apellidos_idx])

        for i, hl in enumerate(headers_lower):
            if hl == "dni":
                return "dni", headers[i]

        return None

    @classmethod
    def _parse_numeric_value(cls, value: str) -> float | None:
        if value is None:
            return None
        cleaned = value.strip()
        if cleaned == "" or cleaned == "-" or cleaned == "N/A":
            return None
        try:
            return float(cleaned.replace(",", "."))
        except (ValueError, TypeError):
            return None

    @classmethod
    def parse_xlsx(cls, content: bytes) -> dict[str, Any]:
        import openpyxl

        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
        ws = wb.active
        if ws is None:
            wb.close()
            raise DomainError("El archivo xlsx no tiene hojas")

        rows_iter = ws.iter_rows(values_only=True)
        headers = [
            str(h).strip() if h is not None else ""
            for h in next(rows_iter, [])
        ]
        if not headers:
            wb.close()
            raise DomainError("El archivo no tiene encabezados")

        result = []
        for row in rows_iter:
            if any(cell is not None and str(cell).strip() != "" for cell in row):
                result.append(
                    {
                        headers[i]: (str(row[i]).strip() if row[i] is not None else "")
                        for i in range(len(headers))
                    }
                )
        wb.close()
        return {"headers": headers, "rows": result}

    @classmethod
    def parse_csv(cls, content: bytes) -> dict[str, Any]:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            raise DomainError("El archivo CSV no contiene datos")
        headers = list(rows[0].keys()) if rows else []
        return {"headers": headers, "rows": rows}

    @classmethod
    def parse_file(cls, content: bytes, filename: str) -> dict[str, Any]:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext == "csv":
            return cls.parse_csv(content)
        elif ext == "xlsx":
            return cls.parse_xlsx(content)
        else:
            raise DomainError(
                "Formato de archivo no soportado. Use .csv o .xlsx"
            )

    @classmethod
    def detect_actividades(
        cls, headers: list[str]
    ) -> list[dict[str, str]]:
        student_result = cls._identify_student_column(headers)
        if student_result is None:
            raise DomainError(
                "No se pudo identificar la columna de alumnos en el archivo"
            )

        if student_result[0] == "email":
            skip_cols = {student_result[1]}
        elif student_result[0] == "nombre_apellidos":
            skip_cols = set(student_result[1])
        else:
            skip_cols = {student_result[1]}

        numeric_cols, textual_cols = cls._detect_column_types(headers)
        actividades = []
        for h in headers:
            if h in skip_cols:
                continue
            if h in numeric_cols:
                actividades.append({"nombre": h, "tipo": "numerica"})
            elif h in textual_cols:
                actividades.append({"nombre": h, "tipo": "textual"})
        return actividades

    @classmethod
    def preview_rows(
        cls, content: bytes, filename: str
    ) -> dict[str, Any]:
        parsed = cls.parse_file(content, filename)
        headers = parsed["headers"]
        rows = parsed["rows"]

        if not rows:
            raise DomainError("El archivo no contiene datos de alumnos")

        actividades = cls.detect_actividades(headers)
        if not actividades:
            raise DomainError(
                "No se detectaron actividades evaluables en el archivo"
            )

        return {
            "actividades": actividades,
            "preview": rows[:5],
            "total_filas": len(rows),
        }


class CalificacionService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._calificacion_repo = CalificacionRepository(tenant_id)
        self._umbral_repo = UmbralRepository(tenant_id)
        self._entrada_repo = EntradaPadronRepository(tenant_id)
        self._version_repo = VersionPadronRepository(tenant_id)
        self._audit_service = AuditLogService(tenant_id)

    def preview(self, content: bytes, filename: str) -> dict[str, Any]:
        return CalificacionParser.preview_rows(content, filename)

    async def importar(
        self,
        db: AsyncSession,
        materia_id: uuid.UUID,
        actividades: list[str],
        content: bytes,
        filename: str,
        usuario_id: uuid.UUID,
    ) -> dict[str, Any]:
        parsed = CalificacionParser.parse_file(content, filename)
        headers = parsed["headers"]
        rows = parsed["rows"]

        if not rows:
            raise DomainError("El archivo no contiene datos de alumnos")

        actividades_detectadas = CalificacionParser.detect_actividades(headers)
        actividad_nombres = {a["nombre"] for a in actividades_detectadas}
        for act in actividades:
            if act not in actividad_nombres:
                raise DomainError(
                    f"Actividad '{act}' no encontrada en el archivo"
                )

        student_info = CalificacionParser._identify_student_column(headers)
        if student_info is None:
            raise DomainError("No se pudo identificar la columna de alumnos")

        if student_info[0] == "email":
            email_col = student_info[1]
            rows_by_id = {}
            for row in rows:
                email_val = row.get(email_col, "").strip().lower()
                if email_val:
                    rows_by_id[email_val] = row
        elif student_info[0] == "nombre_apellidos":
            nombre_col, apellidos_col = student_info[1]
            rows_by_id = {}
            for row in rows:
                key = (
                    row.get(nombre_col, "").strip().lower(),
                    row.get(apellidos_col, "").strip().lower(),
                )
                if key[0] or key[1]:
                    rows_by_id[key] = row
        else:
            dni_col = student_info[1]
            rows_by_id = {}
            for row in rows:
                dni_val = row.get(dni_col, "").strip()
                if dni_val:
                    rows_by_id[dni_val] = row

        versiones_activas = await self._version_repo.get_active_by_materia(db, materia_id)
        if not versiones_activas:
            raise DomainError(
                "No hay un padrón activo para esta materia. Debe importar el padrón primero."
            )
        if len(versiones_activas) > 1:
            raise DomainError(
                "Hay más de un padrón activo para esta materia, no se puede determinar cuál usar."
            )
        version_activa = versiones_activas[0]

        entradas = await self._entrada_repo.get_by_version(
            db, version_activa.id
        )
        entrada_by_email = {}
        entrada_by_nombre_apellido = {}
        for e in entradas:
            email_key = e.email.strip().lower()
            if email_key:
                entrada_by_email[email_key] = e
            name_key = (e.nombre.strip().lower(), e.apellidos.strip().lower())
            entrada_by_nombre_apellido[name_key] = e

        umbral = await self._umbral_repo.get_by_asignacion(db, uuid.UUID(int=0))
        umbral_pct, valores_aprob = self._umbral_repo.get_umbral_efectivo(umbral)
        valores_set = set(valores_aprob) if valores_aprob else set()

        numeric_cols, _ = CalificacionParser._detect_column_types(headers)
        numeric_set = set(numeric_cols)
        selected_set = set(actividades)

        calificaciones_data: list[dict] = []
        errores: list[dict] = []
        advertencias: list[dict] = []
        now = datetime.now(timezone.utc)

        for row_idx, row in enumerate(rows):
            entrada = None
            if student_info[0] == "email":
                email_val = row.get(student_info[1], "").strip().lower()
                entrada = entrada_by_email.get(email_val)
            elif student_info[0] == "nombre_apellidos":
                nombre_col, apellidos_col = student_info[1]
                key = (
                    row.get(nombre_col, "").strip().lower(),
                    row.get(apellidos_col, "").strip().lower(),
                )
                entrada = entrada_by_nombre_apellido.get(key)

            if entrada is None:
                advertencias.append(
                    {
                        "fila": row_idx + 2,
                        "tipo": "sin_identificacion",
                        "detalle": "No se pudo identificar al alumno en el padrón activo",
                    }
                )
                continue

            for act in actividades:
                if act not in row:
                    continue
                if act in selected_set:
                    raw_value = row.get(act, "").strip()
                    nota_num = None
                    nota_text = None
                    aprobado = False

                    if act in numeric_set:
                        nota_num = CalificacionParser._parse_numeric_value(
                            raw_value
                        )
                        if nota_num is None and raw_value:
                            advertencias.append(
                                {
                                    "fila": row_idx + 2,
                                    "tipo": "valor_malformado",
                                    "actividad": act,
                                    "valor": raw_value,
                                    "detalle": "Valor numérico malformado, se registró como null",
                                }
                            )
                        if nota_num is not None:
                            aprobado = nota_num >= umbral_pct
                    else:
                        nota_text = raw_value if raw_value else None
                        if nota_text and valores_set:
                            aprobado = nota_text in valores_set
                        elif nota_text and not valores_set:
                            aprobado = True

                    calificaciones_data.append(
                        {
                            "entrada_padron_id": entrada.id,
                            "materia_id": materia_id,
                            "nombre_actividad": act,
                            "nota_numerica": nota_num,
                            "nota_textual": nota_text,
                            "aprobado": aprobado,
                            "origen": "Importado",
                            "importado_at": now,
                        }
                    )

        if not calificaciones_data:
            raise DomainError(
                "No se generaron calificaciones para importar"
            )

        resultado = await self._calificacion_repo.bulk_upsert(
            db, calificaciones_data
        )

        total = resultado["insertadas"] + resultado["actualizadas"]

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.CALIFICACIONES_IMPORTAR,
            materia_id=materia_id,
            filas_afectadas=total,
            detalle={
                "insertadas": resultado["insertadas"],
                "actualizadas": resultado["actualizadas"],
                "errores": errores,
                "advertencias": advertencias,
            },
        )

        return {
            "insertadas": resultado["insertadas"],
            "actualizadas": resultado["actualizadas"],
            "filas_afectadas": total,
            "errores": errores,
            "advertencias": advertencias,
        }

    async def reporte_finalizacion(
        self,
        db: AsyncSession,
        materia_id: uuid.UUID,
        content: bytes,
        filename: str,
    ) -> dict[str, Any]:
        parsed = CalificacionParser.parse_file(content, filename)
        headers = parsed["headers"]
        rows = parsed["rows"]

        if not rows:
            raise DomainError("El archivo no contiene datos de alumnos")

        actividades = CalificacionParser.detect_actividades(headers)
        textuales = [
            a for a in actividades if a["tipo"] == "textual"
        ]

        versiones_activas = await self._version_repo.get_active_by_materia(db, materia_id)
        if not versiones_activas:
            raise DomainError("No hay un padrón activo para esta materia")
        if len(versiones_activas) > 1:
            raise DomainError(
                "Hay más de un padrón activo para esta materia, no se puede determinar cuál usar."
            )
        version_activa = versiones_activas[0]

        entradas = await self._entrada_repo.get_by_version(
            db, version_activa.id
        )
        entrada_by_email = {}
        entrada_by_nombre = {}
        for e in entradas:
            entrada_by_email[e.email.strip().lower()] = e
            name_key = (e.nombre.strip().lower(), e.apellidos.strip().lower())
            entrada_by_nombre[name_key] = e

        student_info = CalificacionParser._identify_student_column(headers)
        if student_info is None:
            raise DomainError("No se pudo identificar la columna de alumnos")

        entregas_sin_calificar = []

        for row_idx, row in enumerate(rows):
            entrada = None
            if student_info[0] == "email":
                email_val = row.get(student_info[1], "").strip().lower()
                entrada = entrada_by_email.get(email_val)
            elif student_info[0] == "nombre_apellidos":
                nombre_col, apellidos_col = student_info[1]
                key = (
                    row.get(nombre_col, "").strip().lower(),
                    row.get(apellidos_col, "").strip().lower(),
                )
                entrada = entrada_by_nombre.get(key)

            if entrada is None:
                continue

            for ta in textuales:
                raw_value = row.get(ta["nombre"], "").strip().lower()
                if raw_value in ("entregado", "enviado", "submitted"):
                    entregas_sin_calificar.append(
                        {
                            "entrada_padron_id": str(entrada.id),
                            "alumno": f"{entrada.nombre} {entrada.apellidos}",
                            "actividad": ta["nombre"],
                            "valor": raw_value,
                        }
                    )

        return {
            "entregas_sin_calificar": entregas_sin_calificar,
            "total": len(entregas_sin_calificar),
        }
