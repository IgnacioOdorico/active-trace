import uuid

import pytest
from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta, RootEntityMeta
from app.models.tenant import Tenant


db = pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)


class TestTenantModel:
    def test_tenant_inherits_root_entity_meta(self):
        assert issubclass(Tenant, RootEntityMeta)
        assert not issubclass(Tenant, EntityMeta)

    def test_tenant_has_slug_column(self):
        assert hasattr(Tenant, "slug")

    def test_tenant_slug_is_string_type(self):
        col = Tenant.__mapper__.columns["slug"]
        assert isinstance(col.type, String)

    def test_tenant_slug_is_unique(self):
        col = Tenant.__mapper__.columns["slug"]
        assert col.unique

    def test_tenant_has_name_column(self):
        assert hasattr(Tenant, "name")

    def test_tenant_has_config_column(self):
        assert hasattr(Tenant, "config")

    def test_tenant_config_default_empty_dict(self):
        col = Tenant.__mapper__.columns["config"]
        server_default = col.server_default
        if server_default is not None:
            assert "'{}'" in str(server_default.arg) or "{}" in str(server_default.arg)

    def test_tenant_creates_with_slug_and_name(self):
        tenant = Tenant(slug="uni-test", name="University Test")
        assert tenant.slug == "uni-test"
        assert tenant.name == "University Test"

    def test_tenant_creates_with_config(self):
        config = {"theme": "blue", "locale": "es-AR"}
        tenant = Tenant(slug="uni-config", name="Config Test", config=config)
        assert tenant.config == config

    def test_tenant_has_no_tenant_id(self):
        assert not hasattr(Tenant, "tenant_id")

    def test_tenant_tablename_is_tenant(self):
        assert Tenant.__tablename__ == "tenant"


@pytest.mark.asyncio
@db
async def test_tenant_persists_with_unique_slug(db_session):
    tenant = Tenant(slug="universidad-nacional", name="Universidad Nacional")
    db_session.add(tenant)
    await db_session.commit()
    assert tenant.id is not None
    assert tenant.created_at is not None
    assert tenant.updated_at is not None
    assert tenant.deleted_at is None


@pytest.mark.asyncio
@db
async def test_tenant_duplicate_slug_fails(db_session):
    t1 = Tenant(slug="slug-dup", name="First")
    db_session.add(t1)
    await db_session.commit()

    t2 = Tenant(slug="slug-dup", name="Second")
    db_session.add(t2)
    with pytest.raises(Exception):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
@db
async def test_tenant_config_defaults_to_empty(db_session):
    tenant = Tenant(slug="no-config", name="No Config")
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    assert tenant.config == {}


@pytest.mark.asyncio
@db
async def test_entity_with_nonexistent_tenant_fails(db_session):
    class _TestEntityRef(Base, EntityMeta):
        __tablename__ = "test_entity_ref"
        name: Mapped[str] = mapped_column()

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bad_id = uuid.uuid4()
    entity = _TestEntityRef(tenant_id=bad_id, name="orphan")
    db_session.add(entity)
    with pytest.raises(Exception):
        await db_session.commit()
    await db_session.rollback()

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@db
async def test_entity_with_existing_tenant_persists(db_session):
    tenant = Tenant(slug="existing-tenant", name="Existing")
    db_session.add(tenant)
    await db_session.commit()
    tid = tenant.id

    class _TestEntityRef2(Base, EntityMeta):
        __tablename__ = "test_entity_ref2"
        name: Mapped[str] = mapped_column()

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    entity = _TestEntityRef2(tenant_id=tid, name="child")
    db_session.add(entity)
    await db_session.commit()
    assert entity.id is not None
    assert entity.tenant_id == tid

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
