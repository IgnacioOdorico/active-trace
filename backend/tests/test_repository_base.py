import uuid

import pytest
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta
from app.repositories.base import BaseRepository


class _TestRepoEntity(Base, EntityMeta):
    __tablename__ = "test_repo_entity"

    label: Mapped[str] = mapped_column(nullable=False)


class TestBaseRepository:
    def test_instantiate_with_tenant_id(self):
        repo = BaseRepository(_TestRepoEntity, tenant_id=uuid.uuid4())
        assert repo is not None

    def test_instantiate_requires_tenant_id(self):
        with pytest.raises(TypeError):
            BaseRepository(_TestRepoEntity)  # type: ignore[call-arg]

    def test_repo_type_parameter_entity_meta(self):
        repo = BaseRepository(_TestRepoEntity, tenant_id=uuid.uuid4())
        assert repo._model is _TestRepoEntity
        assert repo._tenant_id is not None

    def test_repo_different_tenant_ids(self):
        tid1 = uuid.uuid4()
        tid2 = uuid.uuid4()
        repo1 = BaseRepository(_TestRepoEntity, tenant_id=tid1)
        repo2 = BaseRepository(_TestRepoEntity, tenant_id=tid2)
        assert repo1._tenant_id != repo2._tenant_id

    def test_repo_tenant_id_is_uuid(self):
        repo = BaseRepository(_TestRepoEntity, tenant_id=uuid.uuid4())
        assert isinstance(repo._tenant_id, uuid.UUID)


db = pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)


@pytest.mark.asyncio
@db
async def test_repo_create_persists_with_tenant_id(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "repo-create", "name": "Repo Create"},
    )
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo = BaseRepository(_TestRepoEntity, tenant_id=tid)
    entity = await repo.create(db_session, {"label": "test-entity"})
    assert entity.id is not None
    assert entity.tenant_id == tid
    assert entity.label == "test-entity"

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@db
async def test_repo_get_scoped_to_tenant(db_session):
    from sqlalchemy import text

    tid_a = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid_a, "slug": "repo-get-a", "name": "Repo Get A"},
    )
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo = BaseRepository(_TestRepoEntity, tenant_id=tid_a)
    entity = await repo.create(db_session, {"label": "entity-a"})

    result = await repo.get(db_session, entity.id)
    assert result is not None
    assert result.id == entity.id

    repo_b = BaseRepository(_TestRepoEntity, tenant_id=uuid.uuid4())
    result_b = await repo_b.get(db_session, entity.id)
    assert result_b is None

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@db
async def test_repo_get_excludes_deleted(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "repo-del", "name": "Repo Del"},
    )
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo = BaseRepository(_TestRepoEntity, tenant_id=tid)
    entity = await repo.create(db_session, {"label": "to-delete"})
    await repo.soft_delete(db_session, entity.id)

    result = await repo.get(db_session, entity.id)
    assert result is None

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@db
async def test_repo_get_all_respects_tenant(db_session):
    from sqlalchemy import text

    tid_a = uuid.uuid4()
    tid_b = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid_a, "slug": "repo-all-a", "name": "Repo All A"},
    )
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid_b, "slug": "repo-all-b", "name": "Repo All B"},
    )
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo_a = BaseRepository(_TestRepoEntity, tenant_id=tid_a)
    repo_b = BaseRepository(_TestRepoEntity, tenant_id=tid_b)
    await repo_a.create(db_session, {"label": "a-1"})
    await repo_a.create(db_session, {"label": "a-2"})
    await repo_b.create(db_session, {"label": "b-1"})

    all_a = await repo_a.get_all(db_session)
    assert len(all_a) == 2

    all_b = await repo_b.get_all(db_session)
    assert len(all_b) == 1

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@db
async def test_repo_get_all_include_deleted(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "repo-inc-del", "name": "Repo Inc Del"},
    )
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo = BaseRepository(_TestRepoEntity, tenant_id=tid)
    e1 = await repo.create(db_session, {"label": "active"})
    e2 = await repo.create(db_session, {"label": "deleted"})
    await repo.soft_delete(db_session, e2.id)

    active = await repo.get_all(db_session)
    assert len(active) == 1

    with_deleted = await repo.get_all(db_session, include_deleted=True)
    assert len(with_deleted) == 2

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@db
async def test_repo_update_wrong_tenant_raises_error(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "repo-upd", "name": "Repo Upd"},
    )
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.core.exceptions import EntityNotFoundError

    owner_repo = BaseRepository(_TestRepoEntity, tenant_id=tid)
    entity = await owner_repo.create(db_session, {"label": "owner"})

    other_repo = BaseRepository(_TestRepoEntity, tenant_id=uuid.uuid4())
    with pytest.raises(EntityNotFoundError):
        await other_repo.update(db_session, entity.id, {"label": "hacker"})

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@db
async def test_repo_soft_delete_sets_deleted_at(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "repo-soft", "name": "Repo Soft"},
    )
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo = BaseRepository(_TestRepoEntity, tenant_id=tid)
    entity = await repo.create(db_session, {"label": "soft-me"})
    assert entity.deleted_at is None

    await repo.soft_delete(db_session, entity.id)
    await db_session.refresh(entity)
    assert entity.deleted_at is not None

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@db
async def test_repo_count_active_of_tenant(db_session):
    from sqlalchemy import text

    tid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid, "slug": "repo-count", "name": "Repo Count"},
    )
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo = BaseRepository(_TestRepoEntity, tenant_id=tid)
    await repo.create(db_session, {"label": "c1"})
    await repo.create(db_session, {"label": "c2"})
    e3 = await repo.create(db_session, {"label": "c3"})
    await repo.soft_delete(db_session, e3.id)

    count = await repo.count(db_session)
    assert count == 2

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@db
async def test_repo_multi_tenant_isolation(db_session):
    from sqlalchemy import text

    tid_a = uuid.uuid4()
    tid_b = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid_a, "slug": "iso-a", "name": "Isolation A"},
    )
    await db_session.execute(
        text("INSERT INTO tenant (id, slug, name) VALUES (:id, :slug, :name)"),
        {"id": tid_b, "slug": "iso-b", "name": "Isolation B"},
    )
    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo_a = BaseRepository(_TestRepoEntity, tenant_id=tid_a)
    repo_b = BaseRepository(_TestRepoEntity, tenant_id=tid_b)

    e_a = await repo_a.create(db_session, {"label": "secret-a"})
    await repo_b.create(db_session, {"label": "secret-b"})

    result_a = await repo_a.get(db_session, e_a.id)
    assert result_a is not None

    all_b = await repo_b.get_all(db_session)
    assert all(e.tenant_id == tid_b for e in all_b)
    assert all(e.tenant_id != tid_a for e in all_b)

    async with db_session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
