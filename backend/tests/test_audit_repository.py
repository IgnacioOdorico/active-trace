import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.audit_log import AuditLog
from app.models.user import nombre_completo_usuario
from app.repositories.audit_log import AuditLogRepository


class TestNombreCompletoUsuario:
    def test_concatena_nombre_y_apellidos(self):
        assert nombre_completo_usuario("Ana", "García", "ana@demo.local") == "Ana García"

    def test_usa_email_si_no_hay_nombre_ni_apellidos(self):
        assert nombre_completo_usuario(None, None, "admin@demo.local") == "admin@demo.local"

    def test_usa_solo_nombre_si_no_hay_apellidos(self):
        assert nombre_completo_usuario("Ana", None, "ana@demo.local") == "Ana"


class TestAuditLogRepository:
    def test_instantiate_with_tenant_id(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert repo is not None
        assert repo._tenant_id is not None

    def test_requires_tenant_id(self):
        with pytest.raises(TypeError):
            AuditLogRepository()

    def test_no_update_method(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert not hasattr(repo, "update")

    def test_no_delete_method(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert not hasattr(repo, "delete")

    def test_no_soft_delete_method(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert not hasattr(repo, "soft_delete")

    def test_has_create_method(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert hasattr(repo, "create")
        assert callable(repo.create)

    def test_has_list_method(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert hasattr(repo, "list")
        assert callable(repo.list)

    def test_has_count_method(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert hasattr(repo, "count")
        assert callable(repo.count)

    def test_has_get_method(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert hasattr(repo, "get")
        assert callable(repo.get)

    def test_store_model_is_audit_log(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert repo._model is AuditLog

    def test_different_tenant_ids(self):
        tid1 = uuid.uuid4()
        tid2 = uuid.uuid4()
        repo1 = AuditLogRepository(tenant_id=tid1)
        repo2 = AuditLogRepository(tenant_id=tid2)
        assert repo1._tenant_id != repo2._tenant_id

    def test_tenant_id_is_uuid(self):
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert isinstance(repo._tenant_id, uuid.UUID)


class TestResolucionDeNombres:
    """El panel de auditoria mostraba UUIDs crudos en vez de nombres porque
    docente_nombre/materia_nombre nunca se llenaban (solo el default "" del
    schema). Estos tests fijan que el JOIN contra users/materias resuelve los
    nombres reales."""

    @pytest.fixture
    def repo(self):
        return AuditLogRepository(tenant_id=uuid.uuid4())

    @pytest.mark.asyncio
    async def test_comunicaciones_por_docente_resuelve_nombre(self, repo):
        actor_id = uuid.uuid4()
        row = MagicMock(
            actor_id=actor_id,
            accion="COMUNICACION_ENVIADA",
            total=3,
            nombre="Ana",
            apellidos="García",
            email="ana@demo.local",
        )
        mock_result = MagicMock()
        mock_result.all.return_value = [row]
        session = AsyncMock()
        session.execute = AsyncMock(return_value=mock_result)

        result = await repo.comunicaciones_por_docente(session, desde=None, hasta=None)

        assert result[0]["docente_id"] == str(actor_id)
        assert result[0]["docente_nombre"] == "Ana García"
        assert result[0]["enviado"] == 3

    @pytest.mark.asyncio
    async def test_comunicaciones_por_docente_sin_nombre_usa_email(self, repo):
        actor_id = uuid.uuid4()
        row = MagicMock(
            actor_id=actor_id,
            accion="COMUNICACION_ENVIADA",
            total=1,
            nombre=None,
            apellidos=None,
            email="admin@demo.local",
        )
        mock_result = MagicMock()
        mock_result.all.return_value = [row]
        session = AsyncMock()
        session.execute = AsyncMock(return_value=mock_result)

        result = await repo.comunicaciones_por_docente(session, desde=None, hasta=None)

        assert result[0]["docente_nombre"] == "admin@demo.local"

    @pytest.mark.asyncio
    async def test_interacciones_por_docente_materia_resuelve_nombres(self, repo):
        actor_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        row = MagicMock(
            actor_id=actor_id,
            materia_id=materia_id,
            accion="EVALUACION_CREAR",
            cnt=2,
            nombre="Ana",
            apellidos="García",
            email="ana@demo.local",
            materia_nombre="Matemática I",
        )
        mock_result = MagicMock()
        mock_result.all.return_value = [row]
        session = AsyncMock()
        session.execute = AsyncMock(return_value=mock_result)

        result = await repo.interacciones_por_docente_materia(session, desde=None, hasta=None)

        assert result[0]["docente_nombre"] == "Ana García"
        assert result[0]["materia_nombre"] == "Matemática I"
        assert result[0]["acciones_por_tipo"] == {"EVALUACION_CREAR": 2}

    @pytest.mark.asyncio
    async def test_interacciones_sin_materia_nombre_vacio(self, repo):
        actor_id = uuid.uuid4()
        row = MagicMock(
            actor_id=actor_id,
            materia_id=None,
            accion="LOGIN",
            cnt=1,
            nombre="Ana",
            apellidos="García",
            email="ana@demo.local",
            materia_nombre=None,
        )
        mock_result = MagicMock()
        mock_result.all.return_value = [row]
        session = AsyncMock()
        session.execute = AsyncMock(return_value=mock_result)

        result = await repo.interacciones_por_docente_materia(session, desde=None, hasta=None)

        assert result[0]["materia_id"] == ""
        assert result[0]["materia_nombre"] == ""
