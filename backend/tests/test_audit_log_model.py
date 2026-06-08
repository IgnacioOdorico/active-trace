from app.core.database import Base
from app.models.audit_log import AuditLog
from app.models.base import EntityMeta


class TestAuditLogModel:
    def test_is_not_entity_meta(self):
        assert not issubclass(AuditLog, EntityMeta)

    def test_is_declarative_base(self):
        assert issubclass(AuditLog, Base)

    def test_has_correct_tablename(self):
        assert AuditLog.__tablename__ == "audit_log"

    def test_has_expected_columns(self):
        cols = {c.name for c in AuditLog.__table__.columns}
        expected = {
            "id", "tenant_id", "fecha_hora", "actor_id",
            "impersonado_id", "materia_id", "accion", "detalle",
            "filas_afectadas", "ip", "user_agent",
        }
        assert cols == expected

    def test_no_entity_meta_columns(self):
        cols = {c.name for c in AuditLog.__table__.columns}
        assert "updated_at" not in cols
        assert "deleted_at" not in cols

    def test_has_actor_relationship(self):
        assert hasattr(AuditLog, "actor")

    def test_has_impersonado_relationship(self):
        assert hasattr(AuditLog, "impersonado")

    def test_has_materia_relationship(self):
        assert hasattr(AuditLog, "materia")

    def test_tenant_id_is_foreign_key(self):
        col = AuditLog.__mapper__.columns["tenant_id"]
        assert len(col.foreign_keys) > 0

    def test_actor_id_is_foreign_key(self):
        col = AuditLog.__mapper__.columns["actor_id"]
        assert len(col.foreign_keys) > 0

    def test_impersonado_id_is_nullable(self):
        col = AuditLog.__mapper__.columns["impersonado_id"]
        assert col.nullable

    def test_materia_id_is_nullable(self):
        col = AuditLog.__mapper__.columns["materia_id"]
        assert col.nullable

    def test_detalle_is_nullable(self):
        col = AuditLog.__mapper__.columns["detalle"]
        assert col.nullable

    def test_id_is_primary_key(self):
        col = AuditLog.__mapper__.columns["id"]
        assert col.primary_key

    def test_accion_column_type(self):
        col = AuditLog.__mapper__.columns["accion"]
        assert col.type.length == 100

    def test_fecha_hora_has_timezone(self):
        col = AuditLog.__mapper__.columns["fecha_hora"]
        assert col.type.timezone is True

    def test_ip_column_max_length(self):
        col = AuditLog.__mapper__.columns["ip"]
        assert col.type.length == 45

    def test_user_agent_column_max_length(self):
        col = AuditLog.__mapper__.columns["user_agent"]
        assert col.type.length == 500

    def test_instantiate_with_minimal_fields(self):
        import uuid
        log = AuditLog(tenant_id=uuid.uuid4(), actor_id=uuid.uuid4(), accion="TEST_ACCION")
        assert log.accion == "TEST_ACCION"
        assert log.detalle is None
        assert log.impersonado_id is None
        assert log.materia_id is None
        assert log.ip is None
        assert log.user_agent is None

    def test_filas_afectadas_has_schema_default(self):
        col = AuditLog.__mapper__.columns["filas_afectadas"]
        assert col.default is not None

    def test_instantiate_with_all_fields(self):
        import uuid
        from datetime import datetime, timezone
        tid = uuid.uuid4()
        aid = uuid.uuid4()
        iid = uuid.uuid4()
        mid = uuid.uuid4()
        log = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tid,
            actor_id=aid,
            impersonado_id=iid,
            materia_id=mid,
            accion="TEST_ACCION",
            detalle={"key": "value"},
            filas_afectadas=42,
            ip="192.168.1.1",
            user_agent="test-agent",
        )
        assert log.tenant_id == tid
        assert log.actor_id == aid
        assert log.impersonado_id == iid
        assert log.materia_id == mid
        assert log.detalle == {"key": "value"}
        assert log.filas_afectadas == 42
        assert log.ip == "192.168.1.1"
        assert log.user_agent == "test-agent"
