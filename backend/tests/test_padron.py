import uuid
from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest

from app.core.exceptions import DomainError
from app.models.entrada_padron import EntradaPadron
from app.models.version_padron import VersionPadron


class TestVersionPadronModel:
    def test_tablename(self):
        assert VersionPadron.__tablename__ == "version_padron"

    def test_has_fields(self):
        assert hasattr(VersionPadron, "materia_id")
        assert hasattr(VersionPadron, "cohorte_id")
        assert hasattr(VersionPadron, "cargado_por")
        assert hasattr(VersionPadron, "activa")
        assert hasattr(VersionPadron, "id")
        assert hasattr(VersionPadron, "tenant_id")
        assert hasattr(VersionPadron, "created_at")
        assert hasattr(VersionPadron, "updated_at")
        assert hasattr(VersionPadron, "deleted_at")

    def test_materia_id_fk(self):
        col = VersionPadron.__mapper__.columns["materia_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "materias"

    def test_cohorte_id_fk(self):
        col = VersionPadron.__mapper__.columns["cohorte_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "cohortes"

    def test_cargado_por_fk(self):
        col = VersionPadron.__mapper__.columns["cargado_por"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "users"


class TestEntradaPadronModel:
    def test_tablename(self):
        assert EntradaPadron.__tablename__ == "entrada_padron"

    def test_has_fields(self):
        assert hasattr(EntradaPadron, "version_id")
        assert hasattr(EntradaPadron, "usuario_id")
        assert hasattr(EntradaPadron, "nombre")
        assert hasattr(EntradaPadron, "apellidos")
        assert hasattr(EntradaPadron, "email")
        assert hasattr(EntradaPadron, "comision")
        assert hasattr(EntradaPadron, "regional")
        assert hasattr(EntradaPadron, "id")
        assert hasattr(EntradaPadron, "tenant_id")

    def test_version_id_fk(self):
        col = EntradaPadron.__mapper__.columns["version_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "version_padron"

    def test_usuario_id_nullable(self):
        col = EntradaPadron.__mapper__.columns["usuario_id"]
        assert col.nullable is True


db = pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)


@pytest.fixture
def mock_auth_user():
    return {
        "sub": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "rols": ["COORDINADOR"],
    }


@pytest.fixture
def auth_header(mock_auth_user):
    with patch("app.core.auth.decode_access_token", return_value=mock_auth_user):
        yield {"Authorization": "Bearer fake-token"}


@pytest.fixture
def async_client():
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)
class TestPadronEndpoints:
    @pytest.mark.asyncio
    async def test_import_preview_returns_200(self, async_client, auth_header):
        materia_id = str(uuid.uuid4())
        cohorte_id = str(uuid.uuid4())
        preview_data = {
            "filas_detectadas": 2,
            "columnas": ["nombre", "apellidos", "email", "comision", "regional"],
            "preview": [
                {"nombre": "Juan", "apellidos": "Perez", "email": "juan@test.com", "comision": "A", "regional": "Sur"},
            ],
        }

        with patch("app.routers.padron.PadronService") as MockService:
            mock_svc = MockService.return_value
            mock_svc.preview = AsyncMock(return_value=preview_data)

            response = await async_client.post(
                f"/api/padron/importar?preview=true&materia_id={materia_id}&cohorte_id={cohorte_id}",
                files={"file": ("test.csv", b"nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,A,Sur", "text/csv")},
                headers=auth_header,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["filas_detectadas"] == 2
            assert "preview" in data

    @pytest.mark.asyncio
    async def test_import_confirm_creates_version(self, async_client, auth_header):
        materia_id = str(uuid.uuid4())
        cohorte_id = str(uuid.uuid4())
        version_id = str(uuid.uuid4())

        with patch("app.routers.padron.PadronService") as MockService:
            mock_svc = MockService.return_value
            mock_svc.confirm_import = AsyncMock(
                return_value={
                    "version_id": version_id,
                    "filas_creadas": 2,
                    "mensaje": "Se importaron 2 alumnos correctamente",
                }
            )

            response = await async_client.post(
                f"/api/padron/importar?confirmar=true&materia_id={materia_id}&cohorte_id={cohorte_id}",
                files={"file": ("test.csv", b"nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,A,Sur\nAna,Garcia,ana@test.com,B,Centro", "text/csv")},
                headers=auth_header,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["version_id"] == version_id
            assert data["filas_creadas"] == 2

    @pytest.mark.asyncio
    async def test_import_without_permission_returns_403(self, async_client):
        mock_auth = {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "rols": [],
        }
        with patch("app.core.auth.decode_access_token", return_value=mock_auth):
            response = await async_client.post(
                f"/api/padron/importar?preview=true&materia_id={uuid.uuid4()}&cohorte_id={uuid.uuid4()}",
                files={"file": ("test.csv", b"nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,A,Sur", "text/csv")},
                headers={"Authorization": "Bearer no-perms"},
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_import_invalid_format_returns_422(self, async_client, auth_header):
        with patch("app.routers.padron.PadronService") as MockService:
            mock_svc = MockService.return_value
            mock_svc.preview = AsyncMock(
                side_effect=DomainError("Formato de archivo no soportado")
            )

            response = await async_client.post(
                f"/api/padron/importar?preview=true&materia_id={uuid.uuid4()}&cohorte_id={uuid.uuid4()}",
                files={"file": ("test.txt", b"some,data\n1,2", "text/plain")},
                headers=auth_header,
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_import_missing_preview_or_confirm_returns_400(self, async_client, auth_header):
        with patch("app.routers.padron.PadronService"):
            response = await async_client.post(
                f"/api/padron/importar?materia_id={uuid.uuid4()}&cohorte_id={uuid.uuid4()}",
                files={"file": ("test.csv", b"nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,A,Sur", "text/csv")},
                headers=auth_header,
            )
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_vaciar_materia_returns_204(self, async_client, auth_header):
        materia_id = uuid.uuid4()

        with patch("app.routers.padron.PadronService") as MockService:
            mock_svc = MockService.return_value
            mock_svc.vaciar_materia = AsyncMock()

            response = await async_client.delete(
                f"/api/padron/materia/{materia_id}/vaciar",
                headers=auth_header,
            )
            assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_vaciar_materia_without_permission_returns_403(self, async_client):
        mock_auth = {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "rols": [],
        }
        with patch("app.core.auth.decode_access_token", return_value=mock_auth):
            response = await async_client.delete(
                f"/api/padron/materia/{uuid.uuid4()}/vaciar",
                headers={"Authorization": "Bearer no-perms"},
            )
            assert response.status_code == 403


class TestPadronService:
    def test_parse_csv_valid(self):
        from app.services.padron_service import PadronService
        content = b"nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,A,Sur\nAna,Garcia,ana@test.com,B,Centro"
        result = PadronService.parse_file(content, "test.csv")
        assert len(result) == 2
        assert result[0]["nombre"] == "Juan"
        assert result[0]["email"] == "juan@test.com"

    def test_parse_csv_missing_columns_raises_error(self):
        from app.services.padron_service import PadronService
        content = b"nombre,email\nJuan,juan@test.com"
        with pytest.raises(DomainError, match="Columnas faltantes"):
            PadronService.parse_file(content, "test.csv")

    def test_parse_invalid_format_raises_error(self):
        from app.services.padron_service import PadronService
        content = b"some data"
        with pytest.raises(DomainError, match="no soportado"):
            PadronService.parse_file(content, "test.txt")

    def test_preview_returns_expected_structure(self):
        from app.services.padron_service import PadronService
        svc = PadronService(uuid.uuid4())
        content = b"nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,A,Sur"
        result = svc.preview(content, "test.csv")
        assert result["filas_detectadas"] == 1
        assert "columnas" in result
        assert len(result["preview"]) == 1

    @pytest.mark.asyncio
    async def test_confirm_import_encrypts_email(self):
        from app.services.padron_service import PadronService
        from app.core.security import is_encrypted

        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        content = b"nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,A,Sur"

        with (
            patch("app.services.padron_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.padron_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.padron_service.AuditLogService") as MockAudit,
        ):
            mock_version_repo = MockVersionRepo.return_value
            mock_version_repo.create = AsyncMock(return_value=Mock(id=uuid.uuid4()))
            mock_version_repo._tenant_id = tenant_id

            mock_entrada_repo = MockEntradaRepo.return_value
            mock_entrada_repo.bulk_create = AsyncMock()

            mock_audit = MockAudit.return_value
            mock_audit.log = AsyncMock()

            svc = PadronService(tenant_id)
            result = await svc.confirm_import(
                AsyncMock(),
                materia_id,
                cohorte_id,
                content,
                "test.csv",
                usuario_id,
            )

            assert result["filas_creadas"] == 1
            assert "version_id" in result

            created_entrada = mock_entrada_repo.bulk_create.call_args[0][1][0]
            assert is_encrypted(created_entrada.email)

    @pytest.mark.asyncio
    async def test_confirm_import_generates_audit(self):
        from app.services.padron_service import PadronService

        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        content = b"nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,A,Sur"

        with (
            patch("app.services.padron_service.VersionPadronRepository") as MockVersionRepo,
            patch("app.services.padron_service.EntradaPadronRepository") as MockEntradaRepo,
            patch("app.services.padron_service.AuditLogService") as MockAudit,
        ):
            MockAudit.PADRON_CARGAR = "PADRON_CARGAR"
            MockVersionRepo.return_value.create = AsyncMock(return_value=Mock(id=uuid.uuid4()))
            MockVersionRepo.return_value._tenant_id = tenant_id
            MockEntradaRepo.return_value.bulk_create = AsyncMock()
            mock_audit = MockAudit.return_value
            mock_audit.log = AsyncMock()

            svc = PadronService(tenant_id)
            await svc.confirm_import(
                AsyncMock(), materia_id, cohorte_id, content, "test.csv", usuario_id,
            )

            mock_audit.log.assert_called_once()
            call_kwargs = mock_audit.log.call_args[1]
            assert call_kwargs["accion"] == "PADRON_CARGAR"
            assert call_kwargs["filas_afectadas"] == 1
            assert call_kwargs["materia_id"] == materia_id

    @pytest.mark.asyncio
    async def test_activate_version_deactivates_previous(self):
        from app.services.padron_service import PadronService

        tenant_id = uuid.uuid4()
        version_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()

        mock_version = Mock()
        mock_version.id = version_id
        mock_version.materia_id = materia_id
        mock_version.cohorte_id = cohorte_id

        with patch("app.services.padron_service.VersionPadronRepository") as MockVersionRepo:
            mock_repo = MockVersionRepo.return_value
            mock_repo.get = AsyncMock(return_value=mock_version)
            mock_repo.deactivate_all = AsyncMock()
            mock_repo.update = AsyncMock()

            svc = PadronService(tenant_id)
            await svc.activate_version(AsyncMock(), version_id, tenant_id)

            mock_repo.deactivate_all.assert_called_once()
            mock_repo.update.assert_called_once_with(ANY, version_id, {"activa": True})


@pytest.mark.skipif(
    True,
    reason="Requires external network or mocking",
)
class TestMoodleWSSync:
    @pytest.mark.asyncio
    async def test_sync_users_success(self):
        from app.integrations.moodle_ws import MoodleClient

        mock_users = [{"id": 1, "firstname": "Juan", "lastname": "Perez", "email": "juan@test.com"}]

        with patch.object(MoodleClient, "_call", AsyncMock(return_value=mock_users)):
            client = MoodleClient("https://moodle.test", "token")
            result = await client.sync_users(123)
            assert result == mock_users

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        from app.integrations.moodle_ws import MoodleClient, MoodleWSException

        mock_call = AsyncMock(side_effect=MoodleWSException("error"))

        with patch.object(MoodleClient, "_call", mock_call):
            client = MoodleClient("https://moodle.test", "token", max_retries=3)
            with pytest.raises(MoodleWSException):
                await client.sync_users(123)
            assert mock_call.call_count == 3

    @pytest.mark.asyncio
    async def test_raises_502_after_3_retries(self):
        from app.integrations.moodle_ws import MoodleClient, MoodleWSException

        mock_call = AsyncMock(side_effect=MoodleWSException("Connection refused"))

        with patch.object(MoodleClient, "_call", mock_call):
            client = MoodleClient("https://moodle.test", "token", max_retries=3)
            with pytest.raises(MoodleWSException) as excinfo:
                await client.sync_users(123)
            assert "no disponible" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_sync_with_retry_eventually_succeeds(self):
        from app.integrations.moodle_ws import MoodleClient, MoodleWSException

        mock_users = [{"id": 1, "firstname": "Ana", "email": "ana@test.com"}]
        mock_call = AsyncMock(
            side_effect=[MoodleWSException("timeout"), MoodleWSException("timeout"), mock_users]
        )

        with patch.object(MoodleClient, "_call", mock_call):
            client = MoodleClient("https://moodle.test", "token", max_retries=3)
            result = await client.sync_users(123)
            assert result == mock_users
            assert mock_call.call_count == 3
