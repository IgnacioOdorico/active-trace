from datetime import date, datetime

from pydantic import ValidationError
import pytest


class TestProgramaSchemas:
    def test_create_request_valid(self):
        from app.schemas.programa import ProgramaMateriaCreateRequest
        data = {
            "materia_id": "a" * 32,
            "carrera_id": "b" * 32,
            "cohorte_id": "c" * 32,
            "titulo": "Programa 2026",
            "referencia_archivo": "s3://bucket/programa.pdf",
        }
        req = ProgramaMateriaCreateRequest(**data)
        assert req.titulo == "Programa 2026"

    def test_create_request_requires_all_fields(self):
        from app.schemas.programa import ProgramaMateriaCreateRequest
        with pytest.raises(ValidationError):
            ProgramaMateriaCreateRequest(titulo="incompleto")

    def test_update_request_optional_fields(self):
        from app.schemas.programa import ProgramaMateriaUpdateRequest
        req = ProgramaMateriaUpdateRequest(titulo="Nuevo titulo")
        assert req.titulo == "Nuevo titulo"
        assert req.referencia_archivo is None

    def test_update_request_empty(self):
        from app.schemas.programa import ProgramaMateriaUpdateRequest
        req = ProgramaMateriaUpdateRequest()
        assert req.titulo is None
        assert req.referencia_archivo is None

    def test_response_from_attributes(self):
        from app.schemas.programa import ProgramaMateriaResponse
        now = datetime.now()
        data = {
            "id": "x",
            "materia_id": "a",
            "carrera_id": "b",
            "cohorte_id": "c",
            "titulo": "Prog",
            "referencia_archivo": "ref",
            "cargado_at": now,
            "created_at": now,
            "updated_at": now,
        }
        resp = ProgramaMateriaResponse(**data)
        assert resp.titulo == "Prog"

    def test_list_response(self):
        from app.schemas.programa import ProgramaMateriaListResponse, ProgramaMateriaResponse
        now = datetime.now()
        items = [
            ProgramaMateriaResponse(
                id="1", materia_id="a", carrera_id="b", cohorte_id="c",
                titulo="Prog", referencia_archivo="ref", cargado_at=now,
                created_at=now, updated_at=now,
            )
        ]
        resp = ProgramaMateriaListResponse(items=items, total=1)
        assert resp.total == 1
        assert len(resp.items) == 1


class TestFechaAcademicaSchemas:
    def test_create_request_valid(self):
        from app.schemas.fecha_academica import FechaAcademicaCreateRequest
        data = {
            "materia_id": "a" * 32,
            "cohorte_id": "b" * 32,
            "tipo": "Parcial",
            "numero": 1,
            "periodo": "2026-1",
            "fecha": date(2026, 5, 15),
            "titulo": "Primer Parcial",
        }
        req = FechaAcademicaCreateRequest(**data)
        assert req.tipo == "Parcial"
        assert req.numero == 1

    def test_create_request_requires_all_fields(self):
        from app.schemas.fecha_academica import FechaAcademicaCreateRequest
        with pytest.raises(ValidationError):
            FechaAcademicaCreateRequest(titulo="incompleto")

    def test_update_request_optional_fields(self):
        from app.schemas.fecha_academica import FechaAcademicaUpdateRequest
        req = FechaAcademicaUpdateRequest(titulo="Cambio fecha")
        assert req.titulo == "Cambio fecha"
        assert req.tipo is None

    def test_update_request_empty(self):
        from app.schemas.fecha_academica import FechaAcademicaUpdateRequest
        req = FechaAcademicaUpdateRequest()
        assert all(v is None for v in req.model_dump().values())

    def test_response_from_attributes(self):
        from app.schemas.fecha_academica import FechaAcademicaResponse
        now = datetime.now()
        data = {
            "id": "x",
            "materia_id": "a",
            "cohorte_id": "b",
            "tipo": "Parcial",
            "numero": 1,
            "periodo": "2026-1",
            "fecha": date(2026, 5, 15),
            "titulo": "Primer Parcial",
            "created_at": now,
            "updated_at": now,
        }
        resp = FechaAcademicaResponse(**data)
        assert resp.tipo == "Parcial"

    def test_list_response(self):
        from app.schemas.fecha_academica import FechaAcademicaListResponse, FechaAcademicaResponse
        now = datetime.now()
        items = [
            FechaAcademicaResponse(
                id="1", materia_id="a", cohorte_id="b",
                tipo="TP", numero=1, periodo="2026-1",
                fecha=date(2026, 5, 15), titulo="TP1",
                created_at=now, updated_at=now,
            )
        ]
        resp = FechaAcademicaListResponse(items=items, total=1)
        assert resp.total == 1

    def test_fragmento_lms_response(self):
        from app.schemas.fecha_academica import FragmentoLMSResponse
        resp = FragmentoLMSResponse(html="<table><tr><td>test</td></tr></table>")
        assert "<table>" in resp.html
