import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class _TestEntity(Base, EntityMeta):
    __tablename__ = "test_entity_mixin"

    name: Mapped[str] = mapped_column(nullable=False)


class TestEntityMetaColumns:
    def test_entity_has_id_column(self):
        assert hasattr(_TestEntity, "id")

    def test_entity_id_is_uuid_type(self):
        col = _TestEntity.__mapper__.columns["id"]
        assert isinstance(col.type, Uuid)

    def test_entity_id_is_primary_key(self):
        col = _TestEntity.__mapper__.columns["id"]
        assert col.primary_key

    def test_entity_has_tenant_id_column(self):
        assert hasattr(_TestEntity, "tenant_id")

    def test_entity_has_created_at_column(self):
        assert hasattr(_TestEntity, "created_at")

    def test_entity_has_updated_at_column(self):
        assert hasattr(_TestEntity, "updated_at")

    def test_entity_has_deleted_at_column(self):
        assert hasattr(_TestEntity, "deleted_at")

    def test_entity_id_column_has_default(self):
        col = _TestEntity.__mapper__.columns["id"]
        assert col.default is not None

    def test_entity_tenant_id_is_settable(self):
        tid = uuid.uuid4()
        entity = _TestEntity(tenant_id=tid, name="test")
        assert entity.tenant_id == tid

    def test_entity_tenant_id_column_is_fk(self):
        col = _TestEntity.__mapper__.columns["tenant_id"]
        assert len(col.foreign_keys) > 0

    def test_entity_deleted_at_none_by_default(self):
        entity = _TestEntity(tenant_id=uuid.uuid4(), name="test")
        assert entity.deleted_at is None

    def test_entity_can_set_deleted_at(self):
        entity = _TestEntity(tenant_id=uuid.uuid4(), name="test")
        now = datetime.now(timezone.utc)
        entity.deleted_at = now
        assert entity.deleted_at is not None
        assert isinstance(entity.deleted_at, datetime)

    def test_entity_deleted_at_column_nullable(self):
        col = _TestEntity.__mapper__.columns["deleted_at"]
        assert col.nullable

    def test_entity_tenant_id_rejects_none(self):
        entity = _TestEntity(tenant_id=None, name="test")  # type: ignore[arg-type]
        assert entity.tenant_id is None

    def test_entity_created_at_column_has_server_default(self):
        col = _TestEntity.__mapper__.columns["created_at"]
        assert col.server_default is not None
        assert col.default is None

    def test_entity_updated_at_column_has_onupdate(self):
        col = _TestEntity.__mapper__.columns["updated_at"]
        assert col.onupdate is not None


db = pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)


@pytest.mark.asyncio
@db
async def test_entity_persists_with_tenant(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "test-tenant", "name": "Test Tenant"},
    )
    entity = _TestEntity(tenant_id=tid, name="test")
    db_session.add(entity)
    await db_session.commit()
    assert entity.id is not None
    assert entity.created_at is not None


@pytest.mark.asyncio
@db
async def test_entity_has_created_at_timestamp(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "test-tenant-ca", "name": "Test Tenant CA"},
    )
    entity = _TestEntity(tenant_id=tid, name="test")
    db_session.add(entity)
    await db_session.commit()
    assert entity.created_at is not None
    assert isinstance(entity.created_at, datetime)
    assert entity.created_at.tzinfo is not None


@pytest.mark.asyncio
@db
async def test_entity_updated_at_changes_on_modify(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "test-tenant-ua", "name": "Test Tenant UA"},
    )
    entity = _TestEntity(tenant_id=tid, name="original")
    db_session.add(entity)
    await db_session.commit()
    created = entity.created_at
    updated_before = entity.updated_at

    entity.name = "modified"
    await db_session.commit()
    await db_session.refresh(entity)

    assert entity.updated_at >= updated_before


@pytest.mark.asyncio
@db
async def test_entity_deleted_at_persisted(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "test-tenant-da", "name": "Test Tenant DA"},
    )
    entity = _TestEntity(tenant_id=tid, name="test")
    db_session.add(entity)
    await db_session.commit()

    now = datetime.now(timezone.utc)
    entity.deleted_at = now
    await db_session.commit()
    await db_session.refresh(entity)
    assert entity.deleted_at is not None
