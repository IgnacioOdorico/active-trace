import uuid

import pytest

from app.models.audit_log import AuditLog
from app.repositories.audit_log import AuditLogRepository


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
