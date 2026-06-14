import uuid
from datetime import date, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.exceptions import EntityNotFoundError
from app.schemas.programa import (
    ProgramaMateriaCreateRequest,
    ProgramaMateriaUpdateRequest,
)
from app.schemas.fecha_academica import (
    FechaAcademicaCreateRequest,
    FechaAcademicaUpdateRequest,
)


class TestProgramaService:
    @pytest.mark.asyncio
    async def test_crear_programa_ok(self):
        from app.services.programa_service import ProgramaService

        tenant_id = uuid.uuid4()
        svc = ProgramaService(tenant_id)
        svc._repo = AsyncMock()

        mock_entity = Mock()
        mock_entity.id = uuid.uuid4()
        svc._repo.create = AsyncMock(return_value=mock_entity)

        data = ProgramaMateriaCreateRequest(
            materia_id=str(uuid.uuid4()),
            carrera_id=str(uuid.uuid4()),
            cohorte_id=str(uuid.uuid4()),
            titulo="Programa 2026",
            referencia_archivo="s3://bucket/prog.pdf",
        )
        result = await svc.crear(AsyncMock(), data)

        assert result["id"] == str(mock_entity.id)
        svc._repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_obtener_programa_ok(self):
        from app.services.programa_service import ProgramaService

        tenant_id = uuid.uuid4()
        svc = ProgramaService(tenant_id)
        svc._repo = AsyncMock()

        entity_id = uuid.uuid4()
        mock_entity = Mock()
        mock_entity.id = entity_id
        mock_entity.tenant_id = tenant_id
        mock_entity.materia_id = uuid.uuid4()
        mock_entity.carrera_id = uuid.uuid4()
        mock_entity.cohorte_id = uuid.uuid4()
        mock_entity.titulo = "Programa 2026"
        mock_entity.referencia_archivo = "s3://bucket/prog.pdf"
        mock_entity.cargado_at = datetime.now()
        mock_entity.created_at = datetime.now()
        mock_entity.updated_at = datetime.now()
        svc._repo.get = AsyncMock(return_value=mock_entity)

        result = await svc.obtener(AsyncMock(), entity_id)
        assert result["titulo"] == "Programa 2026"

    @pytest.mark.asyncio
    async def test_obtener_programa_no_existe(self):
        from app.services.programa_service import ProgramaService

        tenant_id = uuid.uuid4()
        svc = ProgramaService(tenant_id)
        svc._repo = AsyncMock()
        svc._repo.get = AsyncMock(return_value=None)

        with pytest.raises(EntityNotFoundError):
            await svc.obtener(AsyncMock(), uuid.uuid4())

    @pytest.mark.asyncio
    async def test_listar_programas(self):
        from app.services.programa_service import ProgramaService

        tenant_id = uuid.uuid4()
        svc = ProgramaService(tenant_id)
        svc._repo = AsyncMock()
        svc._repo.get_all = AsyncMock(return_value=[])

        result = await svc.listar(AsyncMock())
        assert result["total"] == 0
        assert result["items"] == []

    @pytest.mark.asyncio
    async def test_listar_programas_con_filtros(self):
        from app.services.programa_service import ProgramaService

        tenant_id = uuid.uuid4()
        svc = ProgramaService(tenant_id)
        svc._repo = AsyncMock()

        mock_entity = Mock()
        mock_entity.id = uuid.uuid4()
        mock_entity.materia_id = uuid.uuid4()
        mock_entity.carrera_id = uuid.uuid4()
        mock_entity.cohorte_id = uuid.uuid4()
        mock_entity.titulo = "Prog"
        mock_entity.referencia_archivo = "ref"
        mock_entity.cargado_at = datetime.now()
        mock_entity.created_at = datetime.now()
        mock_entity.updated_at = datetime.now()
        svc._repo.get_all = AsyncMock(return_value=[mock_entity])

        result = await svc.listar(AsyncMock(), materia_id=mock_entity.materia_id)
        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_editar_programa_ok(self):
        from app.services.programa_service import ProgramaService

        tenant_id = uuid.uuid4()
        svc = ProgramaService(tenant_id)
        svc._repo = AsyncMock()

        entity_id = uuid.uuid4()
        mock_entity = Mock()
        mock_entity.id = entity_id
        svc._repo.update = AsyncMock(return_value=mock_entity)

        data = ProgramaMateriaUpdateRequest(titulo="Nuevo titulo")
        result = await svc.editar(AsyncMock(), entity_id, data)
        assert result["id"] == str(entity_id)

    @pytest.mark.asyncio
    async def test_eliminar_programa(self):
        from app.services.programa_service import ProgramaService

        tenant_id = uuid.uuid4()
        svc = ProgramaService(tenant_id)
        svc._repo = AsyncMock()
        svc._repo.soft_delete = AsyncMock()

        await svc.eliminar(AsyncMock(), uuid.uuid4())
        svc._repo.soft_delete.assert_called_once()


class TestFechaAcademicaService:
    @pytest.mark.asyncio
    async def test_crear_fecha_ok(self):
        from app.services.fecha_academica_service import FechaAcademicaService

        tenant_id = uuid.uuid4()
        svc = FechaAcademicaService(tenant_id)
        svc._repo = AsyncMock()

        mock_entity = Mock()
        mock_entity.id = uuid.uuid4()
        svc._repo.create = AsyncMock(return_value=mock_entity)

        data = FechaAcademicaCreateRequest(
            materia_id=str(uuid.uuid4()),
            cohorte_id=str(uuid.uuid4()),
            tipo="Parcial",
            numero=1,
            periodo="2026-1",
            fecha=date(2026, 5, 15),
            titulo="Primer Parcial",
        )
        result = await svc.crear(AsyncMock(), data)
        assert result["id"] == str(mock_entity.id)
        svc._repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_obtener_fecha_ok(self):
        from app.services.fecha_academica_service import FechaAcademicaService

        tenant_id = uuid.uuid4()
        svc = FechaAcademicaService(tenant_id)
        svc._repo = AsyncMock()

        entity_id = uuid.uuid4()
        mock_entity = Mock()
        mock_entity.id = entity_id
        mock_entity.tenant_id = tenant_id
        mock_entity.materia_id = uuid.uuid4()
        mock_entity.cohorte_id = uuid.uuid4()
        mock_entity.tipo = "TP"
        mock_entity.numero = 1
        mock_entity.periodo = "2026-1"
        mock_entity.fecha = date(2026, 5, 15)
        mock_entity.titulo = "TP1"
        mock_entity.created_at = datetime.now()
        mock_entity.updated_at = datetime.now()
        svc._repo.get = AsyncMock(return_value=mock_entity)

        result = await svc.obtener(AsyncMock(), entity_id)
        assert result["tipo"] == "TP"

    @pytest.mark.asyncio
    async def test_obtener_fecha_no_existe(self):
        from app.services.fecha_academica_service import FechaAcademicaService

        tenant_id = uuid.uuid4()
        svc = FechaAcademicaService(tenant_id)
        svc._repo = AsyncMock()
        svc._repo.get = AsyncMock(return_value=None)

        with pytest.raises(EntityNotFoundError):
            await svc.obtener(AsyncMock(), uuid.uuid4())

    @pytest.mark.asyncio
    async def test_listar_fechas(self):
        from app.services.fecha_academica_service import FechaAcademicaService

        tenant_id = uuid.uuid4()
        svc = FechaAcademicaService(tenant_id)
        svc._repo = AsyncMock()
        svc._repo.get_all = AsyncMock(return_value=[])

        result = await svc.listar(AsyncMock())
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_editar_fecha_ok(self):
        from app.services.fecha_academica_service import FechaAcademicaService

        tenant_id = uuid.uuid4()
        svc = FechaAcademicaService(tenant_id)
        svc._repo = AsyncMock()

        entity_id = uuid.uuid4()
        mock_entity = Mock()
        mock_entity.id = entity_id
        svc._repo.update = AsyncMock(return_value=mock_entity)

        data = FechaAcademicaUpdateRequest(titulo="Cambio")
        result = await svc.editar(AsyncMock(), entity_id, data)
        assert result["id"] == str(entity_id)

    @pytest.mark.asyncio
    async def test_eliminar_fecha(self):
        from app.services.fecha_academica_service import FechaAcademicaService

        tenant_id = uuid.uuid4()
        svc = FechaAcademicaService(tenant_id)
        svc._repo = AsyncMock()
        svc._repo.soft_delete = AsyncMock()

        await svc.eliminar(AsyncMock(), uuid.uuid4())
        svc._repo.soft_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_generar_fragmento_lms_con_fechas(self):
        from app.services.fecha_academica_service import FechaAcademicaService

        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()
        svc = FechaAcademicaService(tenant_id)
        svc._repo = AsyncMock()

        mock_entity = Mock()
        mock_entity.tipo = "Parcial"
        mock_entity.numero = 1
        mock_entity.fecha = date(2026, 5, 15)
        mock_entity.titulo = "Primer Parcial"
        svc._repo.get_by_materia_cohorte = AsyncMock(return_value=[mock_entity])

        result = await svc.generar_fragmento_lms(
            AsyncMock(), materia_id, cohorte_id
        )
        assert '<table class="fechas-academicas">' in result["html"]
        assert "Parcial" in result["html"]
        assert "Primer Parcial" in result["html"]

    @pytest.mark.asyncio
    async def test_generar_fragmento_lms_sin_fechas(self):
        from app.services.fecha_academica_service import FechaAcademicaService

        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()
        svc = FechaAcademicaService(tenant_id)
        svc._repo = AsyncMock()
        svc._repo.get_by_materia_cohorte = AsyncMock(return_value=[])

        result = await svc.generar_fragmento_lms(
            AsyncMock(), materia_id, cohorte_id
        )
        assert "No hay fechas académicas registradas" in result["html"]
