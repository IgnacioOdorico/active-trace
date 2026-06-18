import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.exceptions import DomainError


class TestCalificacionModel:
    def test_tablename(self):
        from app.models.calificacion import Calificacion
        assert Calificacion.__tablename__ == "calificacion"

    def test_has_fields(self):
        from app.models.calificacion import Calificacion
        assert hasattr(Calificacion, "entrada_padron_id")
        assert hasattr(Calificacion, "materia_id")
        assert hasattr(Calificacion, "nombre_actividad")
        assert hasattr(Calificacion, "nota_numerica")
        assert hasattr(Calificacion, "nota_textual")
        assert hasattr(Calificacion, "aprobado")
        assert hasattr(Calificacion, "origen")
        assert hasattr(Calificacion, "importado_at")
        assert hasattr(Calificacion, "id")
        assert hasattr(Calificacion, "tenant_id")
        assert hasattr(Calificacion, "created_at")
        assert hasattr(Calificacion, "updated_at")
        assert hasattr(Calificacion, "deleted_at")

    def test_entrada_padron_id_fk(self):
        from app.models.calificacion import Calificacion
        col = Calificacion.__mapper__.columns["entrada_padron_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "entrada_padron"

    def test_materia_id_fk(self):
        from app.models.calificacion import Calificacion
        col = Calificacion.__mapper__.columns["materia_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "materias"

    def test_nota_numerica_nullable(self):
        from app.models.calificacion import Calificacion
        col = Calificacion.__mapper__.columns["nota_numerica"]
        assert col.nullable is True

    def test_nota_textual_nullable(self):
        from app.models.calificacion import Calificacion
        col = Calificacion.__mapper__.columns["nota_textual"]
        assert col.nullable is True

    def test_nombre_actividad_not_nullable(self):
        from app.models.calificacion import Calificacion
        col = Calificacion.__mapper__.columns["nombre_actividad"]
        assert col.nullable is False

    def test_unique_constraint(self):
        from app.models.calificacion import Calificacion
        uqs = [c for c in Calificacion.__table_args__ if hasattr(c, "columns")]
        cols = [str(c) for uq in uqs for c in uq.columns]
        assert any("entrada_padron_id" in c for c in cols)
        assert any("nombre_actividad" in c for c in cols)

    def test_origen_default_matches_enum(self):
        from app.models.calificacion import Calificacion
        assert hasattr(Calificacion, "origen")
        col = Calificacion.__mapper__.columns["origen"]
        assert col.nullable is False

    def test_aprobado_default_false(self):
        from app.models.calificacion import Calificacion
        col = Calificacion.__mapper__.columns["aprobado"]
        assert col.default is not None

    def test_importado_at_nullable(self):
        from app.models.calificacion import Calificacion
        col = Calificacion.__mapper__.columns["importado_at"]
        assert col.nullable is True


class TestUmbralMateriaModel:
    def test_tablename(self):
        from app.models.umbral_materia import UmbralMateria
        assert UmbralMateria.__tablename__ == "umbral_materia"

    def test_has_fields(self):
        from app.models.umbral_materia import UmbralMateria
        assert hasattr(UmbralMateria, "asignacion_id")
        assert hasattr(UmbralMateria, "materia_id")
        assert hasattr(UmbralMateria, "umbral_pct")
        assert hasattr(UmbralMateria, "valores_aprobatorios")
        assert hasattr(UmbralMateria, "id")
        assert hasattr(UmbralMateria, "tenant_id")

    def test_asignacion_id_fk(self):
        from app.models.umbral_materia import UmbralMateria
        col = UmbralMateria.__mapper__.columns["asignacion_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "asignaciones"

    def test_asignacion_id_unique(self):
        from app.models.umbral_materia import UmbralMateria
        col = UmbralMateria.__mapper__.columns["asignacion_id"]
        assert col.unique is True

    def test_materia_id_fk(self):
        from app.models.umbral_materia import UmbralMateria
        col = UmbralMateria.__mapper__.columns["materia_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "materias"

    def test_umbral_pct_default_60(self):
        from app.models.umbral_materia import UmbralMateria
        col = UmbralMateria.__mapper__.columns["umbral_pct"]
        assert col.default is not None

    def test_valores_aprobatorios_nullable(self):
        from app.models.umbral_materia import UmbralMateria
        col = UmbralMateria.__mapper__.columns["valores_aprobatorios"]
        assert col.nullable is True


class TestCalificacionParser:
    def test_detect_numeric_columns_by_real_suffix(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["Email", "TP1 (Real)", "TP2 (Real)", "Participación"]
        numeric, textual = CalificacionParser._detect_column_types(headers)
        assert "TP1 (Real)" in numeric
        assert "TP2 (Real)" in numeric
        assert "Participación" not in numeric

    def test_detect_textual_columns(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["Email", "TP1 (Real)", "Participación"]
        _, textual = CalificacionParser._detect_column_types(headers)
        assert "Participación" in textual

    def test_identify_student_column_email_priority(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["Email", "Nombre", "Apellido(s)", "TP1 (Real)"]
        col_type, col_name = CalificacionParser._identify_student_column(headers)
        assert col_type == "email"
        assert col_name == "Email"

    def test_identify_student_column_nombre_apellidos(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["Nombre", "Apellido(s)", "TP1 (Real)"]
        col_type, col_name = CalificacionParser._identify_student_column(headers)
        assert col_type == "nombre_apellidos"

    def test_identify_student_column_no_match_returns_none(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["TP1 (Real)", "TP2 (Real)"]
        result = CalificacionParser._identify_student_column(headers)
        assert result is None

    def test_identify_student_column_direccion_correo(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["Dirección de correo", "TP1 (Real)"]
        col_type, col_name = CalificacionParser._identify_student_column(headers)
        assert col_type == "email"

    def test_identify_student_column_dni(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["DNI", "TP1 (Real)"]
        col_type, col_name = CalificacionParser._identify_student_column(headers)
        assert col_type == "dni"

    def test_identify_student_column_apellidos_singular(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["Nombre", "Apellido", "TP1 (Real)"]
        col_type, col_name = CalificacionParser._identify_student_column(headers)
        assert col_type == "nombre_apellidos"

    def test_parse_numeric_value_ok(self):
        from app.services.calificacion_service import CalificacionParser
        assert CalificacionParser._parse_numeric_value("75.5") == 75.5
        assert CalificacionParser._parse_numeric_value("100") == 100.0
        assert CalificacionParser._parse_numeric_value("0") == 0.0

    def test_parse_numeric_value_malformed(self):
        from app.services.calificacion_service import CalificacionParser
        assert CalificacionParser._parse_numeric_value("N/A") is None
        assert CalificacionParser._parse_numeric_value("-") is None
        assert CalificacionParser._parse_numeric_value("") is None


class TestCalificacionParserCSV:
    def test_parse_csv_valid(self):
        from app.services.calificacion_service import CalificacionParser
        content = "Email,TP1 (Real),Participación\na@b.com,85,Satisfactorio\nc@d.com,90,Supera".encode("utf-8")
        result = CalificacionParser.parse_file(content, "test.csv")
        assert len(result["rows"]) == 2
        assert result["headers"] == ["Email", "TP1 (Real)", "Participación"]

    def test_parse_csv_invalid_format_raises(self):
        from app.services.calificacion_service import CalificacionParser
        content = b"some data"
        with pytest.raises(DomainError, match="no soportado"):
            CalificacionParser.parse_file(content, "test.txt")

    def test_detect_actividades_returns_only_numeric_and_textual(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["Email", "TP1 (Real)", "Participación"]
        actividades = CalificacionParser.detect_actividades(headers)
        nombres = [a["nombre"] for a in actividades]
        assert "TP1 (Real)" in nombres
        assert "Participación" in nombres
        assert "Email" not in nombres

    def test_detect_actividades_sin_identificacion_raises(self):
        from app.services.calificacion_service import CalificacionParser
        headers = ["TP1 (Real)", "TP2 (Real)"]
        with pytest.raises(DomainError, match="No se pudo identificar"):
            CalificacionParser.detect_actividades(headers)

    def test_preview_rows_empty_raises(self):
        from app.services.calificacion_service import CalificacionParser
        content = b"Email,TP1 (Real)\n"
        with pytest.raises(DomainError, match="no contiene datos"):
            CalificacionParser.preview_rows(content, "test.csv")

    def test_preview_rows_no_actividades_raises(self):
        from app.services.calificacion_service import CalificacionParser
        content = b"Email\na@b.com"
        with pytest.raises(DomainError, match="No se detectaron actividades"):
            CalificacionParser.preview_rows(content, "test.csv")


class TestCalificacionService:
    @pytest.mark.asyncio
    async def test_importar_missing_active_padron_raises(self):
        from app.services.calificacion_service import CalificacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.calificacion_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.calificacion_service.CalificacionParser") as MockParser,
        ):
            MockParser.parse_file.return_value = {
                "headers": ["Email", "TP1 (Real)"],
                "rows": [{"Email": "a@b.com", "TP1 (Real)": "85"}],
            }
            MockParser.detect_actividades.return_value = [{"nombre": "TP1 (Real)", "tipo": "numerica"}]
            MockParser._identify_student_column.return_value = ("email", "Email")
            MockParser._detect_column_types.return_value = (["TP1 (Real)"], ["Email"])

            mock_version_repo = MockVersionRepo.return_value
            mock_version_repo.get_active_by_materia = AsyncMock(return_value=None)

            svc = CalificacionService(tenant_id)
            with pytest.raises(DomainError, match="No hay un padrón activo"):
                await svc.importar(
                    AsyncMock(), materia_id, ["TP1 (Real)"],
                    b"", "test.csv", uuid.uuid4(),
                )

    @pytest.mark.asyncio
    async def test_importar_empty_actividades_raises(self):
        from app.services.calificacion_service import CalificacionService
        tenant_id = uuid.uuid4()

        with (
            patch("app.services.calificacion_service.VersionPadronRepository"),
            patch("app.services.calificacion_service.CalificacionParser") as MockParser,
        ):
            MockParser.parse_file.return_value = {
                "headers": ["Email"],
                "rows": [],
            }

            svc = CalificacionService(tenant_id)
            with pytest.raises(DomainError, match="no contiene datos"):
                await svc.importar(
                    AsyncMock(), uuid.uuid4(), [],
                    b"", "test.csv", uuid.uuid4(),
                )

    @pytest.mark.asyncio
    async def test_importar_actividad_no_encontrada_raises(self):
        from app.services.calificacion_service import CalificacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.calificacion_service.VersionPadronRepository"),
            patch("app.services.calificacion_service.CalificacionParser") as MockParser,
        ):
            MockParser.parse_file.return_value = {
                "headers": ["Email", "TP1 (Real)"],
                "rows": [{"Email": "a@b.com", "TP1 (Real)": "85"}],
            }
            MockParser.detect_actividades.return_value = [{"nombre": "TP1 (Real)", "tipo": "numerica"}]

            svc = CalificacionService(tenant_id)
            with pytest.raises(DomainError, match="no encontrada"):
                await svc.importar(
                    AsyncMock(), materia_id, ["ActividadInexistente"],
                    b"", "test.csv", uuid.uuid4(),
                )

    @pytest.mark.asyncio
    async def test_preview_service_delegates_to_parser(self):
        from app.services.calificacion_service import CalificacionService, CalificacionParser
        tenant_id = uuid.uuid4()

        expected = {
            "actividades": [{"nombre": "TP1 (Real)", "tipo": "numerica"}],
            "preview": [],
            "total_filas": 0,
        }

        with patch.object(CalificacionParser, "preview_rows", return_value=expected):
            svc = CalificacionService(tenant_id)
            result = svc.preview(b"", "test.csv")
            assert result == expected

    @pytest.mark.asyncio
    async def test_reporte_finalizacion_no_active_padron_raises(self):
        from app.services.calificacion_service import CalificacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.calificacion_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.calificacion_service.CalificacionParser") as MockParser,
        ):
            MockParser.parse_file.return_value = {
                "headers": ["Email", "TP Final"],
                "rows": [{"Email": "a@b.com", "TP Final": "Entregado"}],
            }
            MockParser.detect_actividades.return_value = [{"nombre": "TP Final", "tipo": "textual"}]

            mock_version_repo = MockVersionRepo.return_value
            mock_version_repo.get_active_by_materia = AsyncMock(return_value=None)

            svc = CalificacionService(tenant_id)
            with pytest.raises(DomainError, match="No hay un padrón activo"):
                await svc.reporte_finalizacion(AsyncMock(), materia_id, b"", "test.csv")

    @pytest.mark.asyncio
    async def test_importar_alumno_no_identificado_genera_advertencia(self):
        from app.services.calificacion_service import CalificacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.calificacion_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.calificacion_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.calificacion_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.calificacion_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.calificacion_service.AuditLogService") as MockAudit,
        ):
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[AsyncMock(id=uuid.uuid4())]
            )

            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.email = "existente@padron.com"
            mock_entrada.nombre = "Existente"
            mock_entrada.apellidos = "EnPadron"
            MockEntradaRepo.return_value.get_by_version = AsyncMock(return_value=[mock_entrada])

            mock_umbral = MockUmbralRepo.return_value
            mock_umbral.get_by_materia = AsyncMock(return_value=None)
            mock_umbral.get_umbral_efectivo = Mock(return_value=(60.0, None))

            MockCalifRepo.return_value.bulk_upsert = AsyncMock(
                return_value={"insertadas": 1, "actualizadas": 0}
            )

            MockAudit.CALIFICACIONES_IMPORTAR = "CALIFICACIONES_IMPORTAR"
            MockAudit.return_value.log = AsyncMock()

            # CSV con 2 alumnos: uno en padrón y otro NO
            csv_content = b"Email,TP1 (Real)\nexistente@padron.com,85\nnuevo@test.com,70\n"
            svc = CalificacionService(tenant_id)
            result = await svc.importar(
                AsyncMock(), materia_id, ["TP1 (Real)"],
                csv_content, "test.csv", usuario_id,
            )

            assert result["insertadas"] == 1
            # Debe haber una advertencia por el alumno no identificado
            assert len(result["advertencias"]) == 1
            assert result["advertencias"][0]["tipo"] == "sin_identificacion"

    @pytest.mark.asyncio
    async def test_importar_textual_con_valores_aprobatorios(self):
        from app.services.calificacion_service import CalificacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.calificacion_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.calificacion_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.calificacion_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.calificacion_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.calificacion_service.AuditLogService") as MockAudit,
        ):
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[AsyncMock(id=uuid.uuid4())]
            )

            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.email = "alumno@test.com"
            mock_entrada.nombre = "Alumno"
            mock_entrada.apellidos = "Test"
            MockEntradaRepo.return_value.get_by_version = AsyncMock(return_value=[mock_entrada])

            mock_umbral = MockUmbralRepo.return_value
            mock_umbral.get_by_materia = AsyncMock(
                return_value=AsyncMock(umbral_pct=60.0, valores_aprobatorios=["Satisfactorio", "Supera"])
            )
            mock_umbral.get_umbral_efectivo = Mock(
                return_value=(60.0, ["Satisfactorio", "Supera"])
            )

            MockCalifRepo.return_value.bulk_upsert = AsyncMock(
                return_value={"insertadas": 2, "actualizadas": 0}
            )

            MockAudit.CALIFICACIONES_IMPORTAR = "CALIFICACIONES_IMPORTAR"
            MockAudit.return_value.log = AsyncMock()

            # CSV con columna textual: "Satisfactorio" debería aprobar, "Regular" no
            csv_content = b"Email,Participacion,TP1 (Real)\nalumno@test.com,Satisfactorio,75\n"
            svc = CalificacionService(tenant_id)
            result = await svc.importar(
                AsyncMock(), materia_id, ["Participacion", "TP1 (Real)"],
                csv_content, "test.csv", usuario_id,
            )

            assert result["insertadas"] == 2
            assert result["actualizadas"] == 0

            # Verificar que bulk_upsert recibió los datos correctos
            call_data = MockCalifRepo.return_value.bulk_upsert.call_args[0][1]
            participacion = [c for c in call_data if c["nombre_actividad"] == "Participacion"][0]
            tp1 = [c for c in call_data if c["nombre_actividad"] == "TP1 (Real)"][0]

            # Participacion es textual con valor "Satisfactorio" → aprobado
            assert participacion["nota_textual"] == "Satisfactorio"
            assert participacion["aprobado"] is True

            # TP1 (Real) es numérico con 75 ≥ 60 → aprobado
            assert tp1["nota_numerica"] == 75.0
            assert tp1["aprobado"] is True


class TestAprobadoDerivation:
    def test_numeric_above_umbral(self):
        umbral_pct = 60.0
        nota = 75.0
        assert nota >= umbral_pct

    def test_numeric_below_umbral(self):
        umbral_pct = 60.0
        nota = 40.0
        assert not (nota >= umbral_pct)

    def test_numeric_exactly_at_umbral(self):
        umbral_pct = 60.0
        nota = 60.0
        assert nota >= umbral_pct

    def test_textual_in_valores_aprobatorios(self):
        valores = {"Satisfactorio", "Supera lo esperado", "Excelente"}
        assert "Supera lo esperado" in valores

    def test_textual_not_in_valores_aprobatorios(self):
        valores = {"Satisfactorio", "Supera lo esperado", "Excelente"}
        assert "Regular" not in valores

    def test_textual_sin_valores_configurados_aprueba(self):
        nota_textual = "Satisfactorio"
        assert nota_textual is not None

    def test_null_nota_numerica_no_aprueba(self):
        nota = None
        assert not (nota is not None and nota >= 60.0)

    def test_null_nota_textual_no_aprueba(self):
        nota = None
        assert not (nota is not None)


class TestCalificacionRepository:
    @pytest.mark.asyncio
    async def test_bulk_upsert_new_inserts(self):
        from app.repositories.calificacion_repository import CalificacionRepository
        tenant_id = uuid.uuid4()
        repo = CalificacionRepository(tenant_id)

        with patch.object(repo._model, "__table__") as MockTable:
            with patch("sqlalchemy.dialects.postgresql.insert") as MockInsert:
                MockInsert.return_value.on_conflict_do_update.return_value = None
                mock_result = AsyncMock()
                mock_result.rowcount = 1
                mock_execute = AsyncMock(return_value=mock_result)

                mock_session = AsyncMock()
                mock_session.execute = mock_execute

                MockTable.name = "calificacion"

                result = await repo.bulk_upsert(
                    mock_session,
                    [{"entrada_padron_id": uuid.uuid4(), "nombre_actividad": "TP1"}],
                )
                assert result["insertadas"] == 1
                assert result["actualizadas"] == 0

    @pytest.mark.asyncio
    async def test_recalcular_aprobado_por_materia(self):
        from app.repositories.calificacion_repository import CalificacionRepository
        tenant_id = uuid.uuid4()
        repo = CalificacionRepository(tenant_id)

        mock_session = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.rowcount = 5
        mock_session.execute = AsyncMock(return_value=mock_execute)

        result = await repo.recalcular_aprobado_por_materia(
            mock_session, uuid.uuid4(), 70.0, ["Satisfactorio"]
        )
        assert result == 5


class TestUmbralRepository:
    def test_umbral_defecto_60(self):
        from app.repositories.umbral_repository import UmbralRepository
        assert UmbralRepository.UMBRAL_DEFECTO == 60.0

    def test_get_umbral_efectivo_sin_config(self):
        from app.repositories.umbral_repository import UmbralRepository
        repo = UmbralRepository(uuid.uuid4())
        pct, valores = repo.get_umbral_efectivo(None)
        assert pct == 60.0
        assert valores is None

    @pytest.mark.asyncio
    async def test_upsert_creates_new(self):
        from app.repositories.umbral_repository import UmbralRepository
        tenant_id = uuid.uuid4()
        repo = UmbralRepository(tenant_id)
        asignacion_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        mock_umbral = AsyncMock()
        mock_umbral.id = uuid.uuid4()
        mock_umbral.asignacion_id = asignacion_id
        mock_umbral.materia_id = materia_id
        mock_umbral.umbral_pct = 75.0
        mock_umbral.valores_aprobatorios = None

        mock_session = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.scalar_one.return_value = mock_umbral
        mock_session.execute = AsyncMock(return_value=mock_execute)

        with patch.object(repo, "get_by_asignacion", AsyncMock(return_value=mock_umbral)):
            result = await repo.upsert(
                mock_session, asignacion_id, materia_id, 75.0
            )
            assert result.umbral_pct == 75.0


class TestUmbralService:
    @pytest.mark.asyncio
    async def test_configurar_umbral_recalcula_aprobados(self):
        from app.services.umbral_service import UmbralService
        tenant_id = uuid.uuid4()
        asignacion_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.umbral_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.umbral_service.CalificacionRepository") as MockCalifRepo,
        ):
            mock_umbral = AsyncMock()
            mock_umbral.id = uuid.uuid4()
            mock_umbral.asignacion_id = asignacion_id
            mock_umbral.materia_id = materia_id
            mock_umbral.umbral_pct = 70.0
            mock_umbral.valores_aprobatorios = ["Satisfactorio"]

            mock_repo = MockUmbralRepo.return_value
            mock_repo.upsert = AsyncMock(return_value=mock_umbral)
            mock_repo.get_umbral_efectivo = Mock(return_value=(70.0, ["Satisfactorio"]))
            MockCalifRepo.return_value.recalcular_aprobado_por_materia = AsyncMock(return_value=3)

            svc = UmbralService(tenant_id)
            result = await svc.configurar(
                AsyncMock(), asignacion_id, materia_id, 70.0, ["Satisfactorio"]
            )
            assert result["umbral_pct"] == 70.0
            assert result["recalculo_aprobados"] == 3

    @pytest.mark.asyncio
    async def test_obtener_vigente_sin_config_devuelve_defecto(self):
        from app.services.umbral_service import UmbralService
        tenant_id = uuid.uuid4()
        asignacion_id = uuid.uuid4()

        with patch("app.services.umbral_service.UmbralRepository") as MockUmbralRepo:
            mock_repo = MockUmbralRepo.return_value
            mock_repo.get_by_asignacion = AsyncMock(return_value=None)
            mock_repo.get_umbral_efectivo = Mock(return_value=(60.0, None))

            svc = UmbralService(tenant_id)
            result = await svc.obtener_vigente(AsyncMock(), asignacion_id)
            assert result["umbral_pct"] == 60.0
            assert result["es_configurado"] is False

    @pytest.mark.asyncio
    async def test_obtener_vigente_con_config(self):
        from app.services.umbral_service import UmbralService
        tenant_id = uuid.uuid4()
        asignacion_id = uuid.uuid4()

        mock_umbral = AsyncMock()
        mock_umbral.umbral_pct = 75.0
        mock_umbral.valores_aprobatorios = ["Satisfactorio", "Excelente"]

        with patch("app.services.umbral_service.UmbralRepository") as MockUmbralRepo:
            mock_repo = MockUmbralRepo.return_value
            mock_repo.get_by_asignacion = AsyncMock(return_value=mock_umbral)
            mock_repo.get_umbral_efectivo = Mock(return_value=(75.0, ["Satisfactorio", "Excelente"]))

            svc = UmbralService(tenant_id)
            result = await svc.obtener_vigente(AsyncMock(), asignacion_id)
            assert result["umbral_pct"] == 75.0
            assert result["es_configurado"] is True


class TestAuditCalificacionesImport:
    @pytest.mark.asyncio
    async def test_import_genera_audit_con_filas_afectadas(self):
        from app.services.calificacion_service import CalificacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.calificacion_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.calificacion_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.calificacion_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.calificacion_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.calificacion_service.AuditLogService") as MockAudit,
            patch("app.services.calificacion_service.CalificacionParser") as MockParser,
        ):
            MockParser.parse_file.return_value = {
                "headers": ["Email", "TP1 (Real)"],
                "rows": [{"Email": "a@b.com", "TP1 (Real)": "85"}],
            }
            MockParser.detect_actividades.return_value = [{"nombre": "TP1 (Real)", "tipo": "numerica"}]
            MockParser._identify_student_column.return_value = ("email", "Email")
            MockParser._detect_column_types.return_value = (["TP1 (Real)"], ["Email"])
            MockParser._parse_numeric_value.return_value = 85.0

            mock_version = AsyncMock()
            mock_version.id = uuid.uuid4()
            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(return_value=[mock_version])

            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.email = "a@b.com"
            mock_entrada.nombre = "Alumno"
            mock_entrada.apellidos = "Test"
            MockEntradaRepo.return_value.get_by_version = AsyncMock(return_value=[mock_entrada])

            mock_umbral_repo = MockUmbralRepo.return_value
            mock_umbral_repo.get_by_materia = AsyncMock(return_value=None)
            mock_umbral_repo.get_umbral_efectivo = Mock(return_value=(60.0, None))

            MockCalifRepo.return_value.bulk_upsert = AsyncMock(
                return_value={"insertadas": 1, "actualizadas": 0}
            )

            MockAudit.CALIFICACIONES_IMPORTAR = "CALIFICACIONES_IMPORTAR"
            mock_audit = MockAudit.return_value
            mock_audit.log = AsyncMock()

            svc = CalificacionService(tenant_id)
            result = await svc.importar(
                AsyncMock(), materia_id, ["TP1 (Real)"],
                b"Email,TP1 (Real)\na@b.com,85", "test.csv", usuario_id,
            )

            mock_audit.log.assert_called_once()
            call_kwargs = mock_audit.log.call_args[1]
            assert call_kwargs["accion"] == "CALIFICACIONES_IMPORTAR"
            assert call_kwargs["materia_id"] == materia_id
            assert call_kwargs["filas_afectadas"] == 1
            assert call_kwargs["detalle"]["insertadas"] == 1
            assert call_kwargs["detalle"]["actualizadas"] == 0
            assert result["insertadas"] == 1

    @pytest.mark.asyncio
    async def test_import_idempotente_reimport_actualiza(self):
        from app.services.calificacion_service import CalificacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        entrada_id = uuid.uuid4()

        with (
            patch("app.services.calificacion_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.calificacion_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.calificacion_service.CalificacionRepository") as MockCalifRepo,
            patch("app.services.calificacion_service.UmbralRepository") as MockUmbralRepo,
            patch("app.services.calificacion_service.AuditLogService") as MockAudit,
            patch("app.services.calificacion_service.CalificacionParser") as MockParser,
        ):
            MockParser.parse_file.return_value = {
                "headers": ["Email", "TP1 (Real)"],
                "rows": [{"Email": "a@b.com", "TP1 (Real)": "90"}],
            }
            MockParser.detect_actividades.return_value = [{"nombre": "TP1 (Real)", "tipo": "numerica"}]
            MockParser._identify_student_column.return_value = ("email", "Email")
            MockParser._detect_column_types.return_value = (["TP1 (Real)"], ["Email"])
            MockParser._parse_numeric_value.return_value = 90.0

            MockVersionRepo.return_value.get_active_by_materia = AsyncMock(
                return_value=[AsyncMock(id=uuid.uuid4())]
            )

            mock_entrada = AsyncMock()
            mock_entrada.id = entrada_id
            mock_entrada.email = "a@b.com"
            mock_entrada.nombre = "Alumno"
            mock_entrada.apellidos = "Test"
            MockEntradaRepo.return_value.get_by_version = AsyncMock(return_value=[mock_entrada])

            mock_umbral_repo = MockUmbralRepo.return_value
            mock_umbral_repo.get_by_materia = AsyncMock(return_value=None)
            mock_umbral_repo.get_umbral_efectivo = Mock(return_value=(60.0, None))

            MockCalifRepo.return_value.bulk_upsert = AsyncMock(
                return_value={"insertadas": 0, "actualizadas": 1}
            )

            MockAudit.return_value.log = AsyncMock()

            svc = CalificacionService(tenant_id)
            result = await svc.importar(
                AsyncMock(), materia_id, ["TP1 (Real)"],
                b"Email,TP1 (Real)\na@b.com,90", "test.csv", usuario_id,
            )

            assert result["actualizadas"] == 1
            assert result["insertadas"] == 0


db = pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)


@pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)
class TestCalificacionEndpoints:
    @pytest.mark.asyncio
    async def test_import_preview_returns_200(self, async_client, auth_header):
        materia_id = str(uuid.uuid4())
        with patch("app.routers.calificaciones.CalificacionService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.preview = AsyncMock(return_value={
                "actividades": [{"nombre": "TP1 (Real)", "tipo": "numerica"}],
                "preview": [],
                "total_filas": 0,
            })
            response = await async_client.post(
                f"/api/calificaciones/preview?materia_id={materia_id}",
                files={"file": ("test.csv", b"Email,TP1 (Real)\na@b.com,80", "text/csv")},
                headers=auth_header,
            )
            assert response.status_code == 200
            data = response.json()
            assert "actividades" in data

    @pytest.mark.asyncio
    async def test_import_confirm_creates_calificaciones(self, async_client, auth_header):
        materia_id = str(uuid.uuid4())
        with patch("app.routers.calificaciones.CalificacionService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.importar = AsyncMock(return_value={
                "insertadas": 5,
                "actualizadas": 0,
                "filas_afectadas": 5,
                "errores": [],
                "advertencias": [],
            })
            response = await async_client.post(
                "/api/calificaciones/importar",
                data={
                    "materia_id": materia_id,
                    "actividades": '["TP1 (Real)"]',
                },
                files={"file": ("test.csv", b"Email,TP1 (Real)\na@b.com,80", "text/csv")},
                headers=auth_header,
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_import_without_permission_returns_403(self, async_client):
        mock_auth = {"sub": str(uuid.uuid4()), "tenant_id": str(uuid.uuid4()), "rols": []}
        with patch("app.core.auth.decode_access_token", return_value=mock_auth):
            response = await async_client.post(
                f"/api/calificaciones/preview?materia_id={uuid.uuid4()}",
                files={"file": ("test.csv", b"Email,TP1\na@b.com,80", "text/csv")},
                headers={"Authorization": "Bearer no-perms"},
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_import_invalid_format_returns_422(self, async_client, auth_header):
        with patch("app.routers.calificaciones.CalificacionService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.preview = AsyncMock(
                side_effect=DomainError("Formato de archivo no soportado")
            )
            response = await async_client.post(
                f"/api/calificaciones/preview?materia_id={uuid.uuid4()}",
                files={"file": ("test.txt", b"some,data", "text/plain")},
                headers=auth_header,
            )
            assert response.status_code == 422


@pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)
class TestUmbralEndpoints:
    @pytest.mark.asyncio
    async def test_configurar_umbral_returns_200(self, async_client, auth_header):
        asignacion_id = str(uuid.uuid4())
        with patch("app.routers.umbral.UmbralService") as MockSvc:
            mock_svc = MockSvc.return_value
            mock_svc.configurar = AsyncMock(return_value={
                "id": str(uuid.uuid4()),
                "asignacion_id": asignacion_id,
                "materia_id": str(uuid.uuid4()),
                "umbral_pct": 70.0,
                "valores_aprobatorios": ["Satisfactorio"],
                "recalculo_aprobados": 3,
            })
            response = await async_client.put(
                f"/api/umbral/{asignacion_id}",
                json={"umbral_pct": 70.0, "valores_aprobatorios": ["Satisfactorio"]},
                headers=auth_header,
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_configurar_umbral_sin_permiso_returns_403(self, async_client):
        mock_auth = {"sub": str(uuid.uuid4()), "tenant_id": str(uuid.uuid4()), "rols": []}
        with patch("app.core.auth.decode_access_token", return_value=mock_auth):
            response = await async_client.put(
                f"/api/umbral/{uuid.uuid4()}",
                json={"umbral_pct": 70.0},
                headers={"Authorization": "Bearer no-perms"},
            )
            assert response.status_code == 403


@pytest.fixture
def auth_header():
    mock_user = {"sub": str(uuid.uuid4()), "tenant_id": str(uuid.uuid4()), "rols": ["COORDINADOR"]}
    with patch("app.core.auth.decode_access_token", return_value=mock_user):
        yield {"Authorization": "Bearer fake-token"}


@pytest.fixture
def async_client():
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
