from datetime import date, time


class TestSlotEncuentroResponse:
    def test_has_fields(self):
        from app.schemas.encuentro import SlotEncuentroResponse
        fields = SlotEncuentroResponse.model_fields
        assert "id" in fields
        assert "asignacion_id" in fields
        assert "materia_id" in fields
        assert "titulo" in fields
        assert "hora" in fields
        assert "dia_semana" in fields
        assert "fecha_inicio" in fields
        assert "cant_semanas" in fields
        assert "fecha_unica" in fields
        assert "meet_url" in fields
        assert "vig_desde" in fields
        assert "vig_hasta" in fields


class TestInstanciaEncuentroResponse:
    def test_has_fields(self):
        from app.schemas.encuentro import InstanciaEncuentroResponse
        fields = InstanciaEncuentroResponse.model_fields
        assert "id" in fields
        assert "slot_id" in fields
        assert "materia_id" in fields
        assert "fecha" in fields
        assert "hora" in fields
        assert "titulo" in fields
        assert "estado" in fields
        assert "meet_url" in fields
        assert "video_url" in fields
        assert "comentario" in fields


class TestInstanciaEncuentroListResponse:
    def test_has_fields(self):
        from app.schemas.encuentro import InstanciaEncuentroListResponse
        fields = InstanciaEncuentroListResponse.model_fields
        assert "items" in fields
        assert "total" in fields
        assert "pagina" in fields
        assert "page_size" in fields


class TestCrearSlotRecurrenteRequest:
    def test_has_fields(self):
        from app.schemas.encuentro import CrearSlotRecurrenteRequest
        fields = CrearSlotRecurrenteRequest.model_fields
        assert "materia_id" in fields
        assert "titulo" in fields
        assert "hora" in fields
        assert "dia_semana" in fields
        assert "fecha_inicio" in fields
        assert "cant_semanas" in fields
        assert "meet_url" in fields
        assert "vig_desde" in fields

    def test_materia_id_is_str(self):
        from app.schemas.encuentro import CrearSlotRecurrenteRequest
        assert CrearSlotRecurrenteRequest.model_fields["materia_id"].annotation is str

    def test_cant_semanas_default_0(self):
        from app.schemas.encuentro import CrearSlotRecurrenteRequest
        field = CrearSlotRecurrenteRequest.model_fields["cant_semanas"]
        assert field.default == 0


class TestCrearEncuentroUnicoRequest:
    def test_has_fields(self):
        from app.schemas.encuentro import CrearEncuentroUnicoRequest
        fields = CrearEncuentroUnicoRequest.model_fields
        assert "materia_id" in fields
        assert "fecha" in fields
        assert "hora" in fields
        assert "titulo" in fields
        assert "meet_url" in fields


class TestEditarInstanciaRequest:
    def test_has_fields(self):
        from app.schemas.encuentro import EditarInstanciaRequest
        fields = EditarInstanciaRequest.model_fields
        assert "estado" in fields
        assert "meet_url" in fields
        assert "video_url" in fields
        assert "comentario" in fields

    def test_optional_fields(self):
        from app.schemas.encuentro import EditarInstanciaRequest
        assert EditarInstanciaRequest.model_fields["estado"].default is None
        assert EditarInstanciaRequest.model_fields["meet_url"].default is None
        assert EditarInstanciaRequest.model_fields["video_url"].default is None
        assert EditarInstanciaRequest.model_fields["comentario"].default is None


class TestGenerarHTMLResponse:
    def test_has_html_field(self):
        from app.schemas.encuentro import GenerarHTMLResponse
        assert "html" in GenerarHTMLResponse.model_fields


class TestGuardiaResponse:
    def test_has_fields(self):
        from app.schemas.guardia import GuardiaResponse
        fields = GuardiaResponse.model_fields
        assert "id" in fields
        assert "asignacion_id" in fields
        assert "materia_id" in fields
        assert "carrera_id" in fields
        assert "cohorte_id" in fields
        assert "dia" in fields
        assert "horario" in fields
        assert "estado" in fields
        assert "comentarios" in fields


class TestGuardiaListResponse:
    def test_has_fields(self):
        from app.schemas.guardia import GuardiaListResponse
        fields = GuardiaListResponse.model_fields
        assert "items" in fields
        assert "total" in fields
        assert "pagina" in fields
        assert "page_size" in fields


class TestCrearGuardiaRequest:
    def test_has_fields(self):
        from app.schemas.guardia import CrearGuardiaRequest
        fields = CrearGuardiaRequest.model_fields
        assert "materia_id" in fields
        assert "carrera_id" in fields
        assert "dia" in fields
        assert "horario" in fields

    def test_cohorte_id_optional(self):
        from app.schemas.guardia import CrearGuardiaRequest
        assert CrearGuardiaRequest.model_fields["cohorte_id"].default is None

    def test_comentarios_optional(self):
        from app.schemas.guardia import CrearGuardiaRequest
        assert CrearGuardiaRequest.model_fields["comentarios"].default is None


class TestEditarGuardiaRequest:
    def test_has_fields(self):
        from app.schemas.guardia import EditarGuardiaRequest
        fields = EditarGuardiaRequest.model_fields
        assert "estado" in fields
        assert "comentarios" in fields

    def test_optional_fields(self):
        from app.schemas.guardia import EditarGuardiaRequest
        assert EditarGuardiaRequest.model_fields["comentarios"].default is None


class TestExportGuardiasResponse:
    def test_has_fields(self):
        from app.schemas.guardia import ExportGuardiasResponse
        fields = ExportGuardiasResponse.model_fields
        assert "items" in fields
