import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import DomainError, EntityNotFoundError
from app.schemas.estructura import (
    CarreraCreate,
    CarreraUpdate,
    CohorteCreate,
    CohorteUpdate,
    MateriaCreate,
    MateriaUpdate,
)
from app.services.carrera_service import CarreraService
from app.services.cohorte_service import CohorteService
from app.services.materia_service import MateriaService


@pytest.fixture
def tenant_id():
    return uuid.uuid4()


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
def mock_execute(mock_db):
    result = MagicMock()
    mock_db.execute.return_value = result
    return result


class TestCarreraService:
    def test_init(self, tenant_id):
        svc = CarreraService(tenant_id)
        assert svc._tenant_id == tenant_id

    @pytest.mark.asyncio
    async def test_create_duplicate_codigo_raises(
        self, tenant_id, mock_db, mock_execute
    ):
        mock_execute.scalar_one_or_none.return_value = MagicMock()

        svc = CarreraService(tenant_id)
        data = CarreraCreate(codigo="ING", nombre="Ingeniería")

        with pytest.raises(DomainError, match="Ya existe una carrera"):
            await svc.create(mock_db, data)

    @pytest.mark.asyncio
    async def test_create_success(
        self, tenant_id, mock_db, mock_execute
    ):
        mock_execute.scalar_one_or_none.return_value = None

        mock_entity = MagicMock()
        mock_entity.id = uuid.uuid4()
        mock_entity.codigo = "ING"

        svc = CarreraService(tenant_id)
        with patch.object(svc._repo, "create", AsyncMock(return_value=mock_entity)):
            data = CarreraCreate(codigo="ING", nombre="Ingeniería")
            result = await svc.create(mock_db, data)
            assert result.codigo == "ING"

    @pytest.mark.asyncio
    async def test_get_not_found_raises(self, tenant_id, mock_db):
        svc = CarreraService(tenant_id)
        with patch.object(svc._repo, "get", AsyncMock(return_value=None)):
            with pytest.raises(EntityNotFoundError):
                await svc.get(mock_db, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_success(self, tenant_id, mock_db):
        mock_entity = MagicMock()
        mock_entity.id = uuid.uuid4()

        svc = CarreraService(tenant_id)
        with patch.object(svc._repo, "get", AsyncMock(return_value=mock_entity)):
            result = await svc.get(mock_db, mock_entity.id)
            assert result.id == mock_entity.id

    @pytest.mark.asyncio
    async def test_get_all(self, tenant_id, mock_db):
        svc = CarreraService(tenant_id)
        with patch.object(svc._repo, "get_all", AsyncMock(return_value=[])):
            result = await svc.get_all(mock_db)
            assert result == []

    @pytest.mark.asyncio
    async def test_update_success(self, tenant_id, mock_db):
        mock_entity = MagicMock()
        mock_entity.nombre = "Updated"

        svc = CarreraService(tenant_id)
        with patch.object(svc._repo, "update", AsyncMock(return_value=mock_entity)):
            data = CarreraUpdate(nombre="Updated")
            result = await svc.update(mock_db, uuid.uuid4(), data)
            assert result.nombre == "Updated"

    @pytest.mark.asyncio
    async def test_soft_delete(self, tenant_id, mock_db):
        svc = CarreraService(tenant_id)
        with patch.object(svc._repo, "soft_delete", AsyncMock()) as mock_delete:
            await svc.soft_delete(mock_db, uuid.uuid4())
            mock_delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_validate_activa_raises_when_inactive(self, tenant_id, mock_db):
        mock_entity = MagicMock()
        mock_entity.activa = False

        svc = CarreraService(tenant_id)
        with patch.object(svc._repo, "get", AsyncMock(return_value=mock_entity)):
            with pytest.raises(DomainError, match="no está activa"):
                await svc.validate_activa(mock_db, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_validate_activa_success(self, tenant_id, mock_db):
        mock_entity = MagicMock()
        mock_entity.activa = True

        svc = CarreraService(tenant_id)
        with patch.object(svc._repo, "get", AsyncMock(return_value=mock_entity)):
            result = await svc.validate_activa(mock_db, uuid.uuid4())
            assert result.activa is True


class TestCohorteService:
    @pytest.mark.asyncio
    async def test_create_validates_carrera_activa(self, tenant_id, mock_db):
        svc = CohorteService(tenant_id)
        data = CohorteCreate(
            nombre="2026A",
            carrera_id=str(uuid.uuid4()),
            fecha_inicio=datetime.now(timezone.utc),
            fecha_fin=datetime.now(timezone.utc),
        )

        with patch.object(svc._carrera_svc, "validate_activa", AsyncMock(side_effect=DomainError("La carrera no está activa"))):
            with pytest.raises(DomainError, match="no está activa"):
                await svc.create(mock_db, data)

    @pytest.mark.asyncio
    async def test_create_duplicate_nombre_raises(
        self, tenant_id, mock_db, mock_execute
    ):
        mock_execute.scalar_one_or_none.return_value = MagicMock()

        svc = CohorteService(tenant_id)
        data = CohorteCreate(
            nombre="2026A",
            carrera_id=str(uuid.uuid4()),
            fecha_inicio=datetime.now(timezone.utc),
            fecha_fin=datetime.now(timezone.utc),
        )

        with patch.object(svc._carrera_svc, "validate_activa", AsyncMock()):
            with pytest.raises(DomainError, match="Ya existe un cohorte"):
                await svc.create(mock_db, data)

    @pytest.mark.asyncio
    async def test_create_success(
        self, tenant_id, mock_db, mock_execute
    ):
        mock_execute.scalar_one_or_none.side_effect = [None, None]

        mock_entity = MagicMock()
        mock_entity.nombre = "2026A"

        svc = CohorteService(tenant_id)
        with patch.object(svc._carrera_svc, "validate_activa", AsyncMock()):
            with patch.object(svc._repo, "create", AsyncMock(return_value=mock_entity)):
                data = CohorteCreate(
                    nombre="2026A",
                    carrera_id=str(uuid.uuid4()),
                    fecha_inicio=datetime.now(timezone.utc),
                    fecha_fin=datetime.now(timezone.utc),
                )
                result = await svc.create(mock_db, data)
                assert result.nombre == "2026A"

    @pytest.mark.asyncio
    async def test_get_not_found_raises(self, tenant_id, mock_db):
        svc = CohorteService(tenant_id)
        with patch.object(svc._repo, "get", AsyncMock(return_value=None)):
            with pytest.raises(EntityNotFoundError):
                await svc.get(mock_db, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_all_with_carrera_filter(self, tenant_id, mock_db):
        svc = CohorteService(tenant_id)
        carrera_id = uuid.uuid4()
        with patch.object(svc._repo, "get_all", AsyncMock(return_value=[])):
            result = await svc.get_all(mock_db, carrera_id=carrera_id)
            assert result == []

    @pytest.mark.asyncio
    async def test_get_all_no_filter(self, tenant_id, mock_db):
        svc = CohorteService(tenant_id)
        with patch.object(svc._repo, "get_all", AsyncMock(return_value=[])):
            result = await svc.get_all(mock_db)
            assert result == []

    @pytest.mark.asyncio
    async def test_update_success(self, tenant_id, mock_db):
        mock_entity = MagicMock()
        mock_entity.nombre = "2026B"

        svc = CohorteService(tenant_id)
        with patch.object(svc._repo, "update", AsyncMock(return_value=mock_entity)):
            data = CohorteUpdate(nombre="2026B")
            result = await svc.update(mock_db, uuid.uuid4(), data)
            assert result.nombre == "2026B"

    @pytest.mark.asyncio
    async def test_soft_delete(self, tenant_id, mock_db):
        svc = CohorteService(tenant_id)
        with patch.object(svc._repo, "soft_delete", AsyncMock()) as mock_delete:
            await svc.soft_delete(mock_db, uuid.uuid4())
            mock_delete.assert_awaited_once()


class TestMateriaService:
    @pytest.mark.asyncio
    async def test_create_duplicate_codigo_raises(
        self, tenant_id, mock_db, mock_execute
    ):
        mock_execute.scalar_one_or_none.return_value = MagicMock()

        svc = MateriaService(tenant_id)
        data = MateriaCreate(codigo="MAT01", nombre="Matemáticas")

        with pytest.raises(DomainError, match="Ya existe una materia"):
            await svc.create(mock_db, data)

    @pytest.mark.asyncio
    async def test_create_without_carrera(
        self, tenant_id, mock_db, mock_execute
    ):
        mock_execute.scalar_one_or_none.return_value = None

        mock_entity = MagicMock()
        mock_entity.codigo = "MAT01"
        mock_entity.carrera_id = None

        svc = MateriaService(tenant_id)
        with patch.object(svc._repo, "create", AsyncMock(return_value=mock_entity)):
            data = MateriaCreate(codigo="MAT01", nombre="Matemáticas")
            result = await svc.create(mock_db, data)
            assert result.carrera_id is None

    @pytest.mark.asyncio
    async def test_create_with_carrera(
        self, tenant_id, mock_db, mock_execute
    ):
        mock_execute.scalar_one_or_none.return_value = None

        carrera_id = uuid.uuid4()
        mock_entity = MagicMock()
        mock_entity.codigo = "MAT01"
        mock_entity.carrera_id = carrera_id

        svc = MateriaService(tenant_id)
        with patch.object(svc._repo, "create", AsyncMock(return_value=mock_entity)):
            data = MateriaCreate(codigo="MAT01", nombre="Matemáticas", carrera_id=str(carrera_id))
            result = await svc.create(mock_db, data)
            assert result.carrera_id == carrera_id

    @pytest.mark.asyncio
    async def test_get_not_found_raises(self, tenant_id, mock_db):
        svc = MateriaService(tenant_id)
        with patch.object(svc._repo, "get", AsyncMock(return_value=None)):
            with pytest.raises(EntityNotFoundError):
                await svc.get(mock_db, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_all_with_carrera_filter(self, tenant_id, mock_db):
        svc = MateriaService(tenant_id)
        carrera_id = uuid.uuid4()
        with patch.object(svc._repo, "get_all", AsyncMock(return_value=[])):
            result = await svc.get_all(mock_db, carrera_id=carrera_id)
            assert result == []

    @pytest.mark.asyncio
    async def test_get_all_no_filter(self, tenant_id, mock_db):
        svc = MateriaService(tenant_id)
        with patch.object(svc._repo, "get_all", AsyncMock(return_value=[])):
            result = await svc.get_all(mock_db)
            assert result == []

    @pytest.mark.asyncio
    async def test_update_success(self, tenant_id, mock_db):
        mock_entity = MagicMock()
        mock_entity.nombre = "Updated"

        svc = MateriaService(tenant_id)
        with patch.object(svc._repo, "update", AsyncMock(return_value=mock_entity)):
            data = MateriaUpdate(nombre="Updated")
            result = await svc.update(mock_db, uuid.uuid4(), data)
            assert result.nombre == "Updated"

    @pytest.mark.asyncio
    async def test_soft_delete(self, tenant_id, mock_db):
        svc = MateriaService(tenant_id)
        with patch.object(svc._repo, "soft_delete", AsyncMock()) as mock_delete:
            await svc.soft_delete(mock_db, uuid.uuid4())
            mock_delete.assert_awaited_once()
