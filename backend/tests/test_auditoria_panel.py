from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.api.v1.routers.auditoria_panel import _resolve_panel_permission
from app.core.dependencies import get_current_user, get_db
from app.models.audit_log import AuditLog
from app.schemas.auditoria_panel import (
    AccionesPorDiaItem,
    ComunicacionesPorDocenteItem,
    InteraccionesPorDocenteMateriaItem,
    UltimasAccionesResponse,
)


class MockUser:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.tenant_id = kwargs.get("tenant_id", uuid.uuid4())
        self.email = kwargs.get("email", "test@test.com")
        self.is_active = True


def _make_mock_db(result_list=None, total=0):
    mock_db = AsyncMock(spec=["execute", "close"])
    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = result_list or []
    mock_result.scalar_one.return_value = total
    mock_result.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.close = AsyncMock()
    return mock_db


# ============================================================
# Schemas
# ============================================================

class TestAccionesPorDiaItem:
    def test_all_fields(self):
        item = AccionesPorDiaItem(fecha=date(2026, 6, 1), total=42)
        assert item.fecha == date(2026, 6, 1)
        assert item.total == 42

    def test_serialization(self):
        item = AccionesPorDiaItem(fecha=date(2026, 6, 1), total=5)
        data = item.model_dump()
        assert data["fecha"] == date(2026, 6, 1)
        assert data["total"] == 5


class TestComunicacionesPorDocenteItem:
    def test_all_fields(self):
        item = ComunicacionesPorDocenteItem(
            docente_id="uuid-1", pendiente=2, enviando=3, enviado=10, fallido=1, cancelado=0
        )
        assert item.docente_id == "uuid-1"
        assert item.pendiente == 2
        assert item.enviando == 3
        assert item.enviado == 10
        assert item.fallido == 1
        assert item.cancelado == 0

    def test_defaults(self):
        item = ComunicacionesPorDocenteItem(docente_id="uuid-1")
        assert item.docente_nombre == ""
        assert item.pendiente == 0
        assert item.enviando == 0
        assert item.enviado == 0
        assert item.fallido == 0
        assert item.cancelado == 0


class TestInteraccionesPorDocenteMateriaItem:
    def test_all_fields(self):
        item = InteraccionesPorDocenteMateriaItem(
            docente_id="uuid-doc",
            materia_id="uuid-mat",
            total_acciones=15,
            acciones_por_tipo={"ACCION_A": 10, "ACCION_B": 5},
        )
        assert item.docente_id == "uuid-doc"
        assert item.materia_id == "uuid-mat"
        assert item.total_acciones == 15
        assert item.acciones_por_tipo == {"ACCION_A": 10, "ACCION_B": 5}

    def test_defaults(self):
        item = InteraccionesPorDocenteMateriaItem(
            docente_id="uuid-doc",
            materia_id="uuid-mat",
            total_acciones=0,
            acciones_por_tipo={},
        )
        assert item.docente_nombre == ""
        assert item.materia_nombre == ""


class TestUltimasAccionesResponse:
    def test_all_fields(self):
        from app.schemas.audit import AuditLogResponse
        now = datetime.now()
        log = AuditLogResponse(
            id="id-1", fecha_hora=now, actor_id="actor-1", accion="TEST", filas_afectadas=0
        )
        resp = UltimasAccionesResponse(items=[log], max_resultados=200)
        assert len(resp.items) == 1
        assert resp.max_resultados == 200

    def test_empty_items(self):
        resp = UltimasAccionesResponse(items=[], max_resultados=100)
        assert resp.items == []
        assert resp.max_resultados == 100


# ============================================================
# Repository methods
# ============================================================

class TestAuditLogRepositoryNewMethods:
    def test_repo_has_acciones_por_dia(self):
        from app.repositories.audit_log import AuditLogRepository
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert hasattr(repo, "acciones_por_dia")
        assert callable(repo.acciones_por_dia)

    def test_repo_has_comunicaciones_por_docente(self):
        from app.repositories.audit_log import AuditLogRepository
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert hasattr(repo, "comunicaciones_por_docente")
        assert callable(repo.comunicaciones_por_docente)

    def test_repo_has_interacciones_por_docente_materia(self):
        from app.repositories.audit_log import AuditLogRepository
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert hasattr(repo, "interacciones_por_docente_materia")
        assert callable(repo.interacciones_por_docente_materia)

    def test_repo_has_ultimas_acciones(self):
        from app.repositories.audit_log import AuditLogRepository
        repo = AuditLogRepository(tenant_id=uuid.uuid4())
        assert hasattr(repo, "ultimas_acciones")
        assert callable(repo.ultimas_acciones)


# ============================================================
# Service methods
# ============================================================

class TestAuditLogServiceNewMethods:
    def test_svc_has_acciones_por_dia(self):
        from app.services.audit_service import AuditLogService
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert hasattr(svc, "acciones_por_dia")
        assert callable(svc.acciones_por_dia)

    def test_svc_has_comunicaciones_por_docente(self):
        from app.services.audit_service import AuditLogService
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert hasattr(svc, "comunicaciones_por_docente")
        assert callable(svc.comunicaciones_por_docente)

    def test_svc_has_interacciones_por_docente_materia(self):
        from app.services.audit_service import AuditLogService
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert hasattr(svc, "interacciones_por_docente_materia")
        assert callable(svc.interacciones_por_docente_materia)

    def test_svc_has_ultimas_acciones(self):
        from app.services.audit_service import AuditLogService
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert hasattr(svc, "ultimas_acciones")
        assert callable(svc.ultimas_acciones)

    @pytest.mark.asyncio
    async def test_svc_ultimas_acciones_passes_max_resultados(self):
        from app.services.audit_service import AuditLogService
        mock_repo = AsyncMock()
        svc = AuditLogService(tenant_id=uuid.uuid4())
        svc._repo = mock_repo
        mock_repo.ultimas_acciones = AsyncMock(return_value=[])
        result = await svc.ultimas_acciones(
            AsyncMock(), max_resultados=50, desde=None, hasta=None
        )
        assert result == []
        mock_repo.ultimas_acciones.assert_called_once()
        args, kwargs = mock_repo.ultimas_acciones.call_args
        assert kwargs["max_resultados"] == 50


# ============================================================
# Router — permission dependency
# ============================================================

class TestResolvePanelPermission:
    @pytest.mark.asyncio
    async def test_requires_auth(self):
        request = MagicMock()
        request.headers = {}
        db = _make_mock_db()
        with pytest.raises(Exception):
            await _resolve_panel_permission(request, db, MockUser())


# ============================================================
# Router — endpoint registration
# ============================================================

class TestAuditoriaPanelRouter:
    @pytest.mark.asyncio
    async def test_endpoint_paths_registered(self):
        from app.api.v1.routers.auditoria_panel import router
        paths = [r.path for r in router.routes]
        assert "/api/v1/admin/panel/acciones-por-dia" in paths
        assert "/api/v1/admin/panel/comunicaciones-por-docente" in paths
        assert "/api/v1/admin/panel/interacciones-por-docente-materia" in paths
        assert "/api/v1/admin/panel/ultimas-acciones" in paths

    @pytest.mark.asyncio
    async def test_router_tag(self):
        from app.api.v1.routers.auditoria_panel import router
        assert "auditoria-panel" in router.tags

    @pytest.mark.asyncio
    async def test_router_prefix(self):
        from app.api.v1.routers.auditoria_panel import router
        assert router.prefix == "/api/v1/admin/panel"

    @pytest.mark.asyncio
    async def test_requires_auth(self, async_client: AsyncClient):
        from app.main import app
        mock_db = _make_mock_db()
        app.dependency_overrides[get_db] = lambda: mock_db
        try:
            response = await async_client.get("/api/v1/admin/panel/acciones-por-dia")
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_acciones_por_dia_returns_list(self, async_client: AsyncClient):
        from app.main import app
        user = MockUser()
        mock_db = _make_mock_db()
        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[_resolve_panel_permission] = lambda: (True, None)
        try:
            response = await async_client.get(
                "/api/v1/admin/panel/acciones-por-dia",
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 200
            assert isinstance(response.json(), list)
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_ultimas_acciones_returns_structure(self, async_client: AsyncClient):
        from app.main import app
        user = MockUser()
        mock_db = _make_mock_db()
        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[_resolve_panel_permission] = lambda: (True, None)
        try:
            response = await async_client.get(
                "/api/v1/admin/panel/ultimas-acciones",
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 200
            body = response.json()
            assert "items" in body
            assert "max_resultados" in body
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_forbidden_without_permission(self, async_client: AsyncClient):
        from app.main import app
        mock_db = _make_mock_db()
        app.dependency_overrides[get_db] = lambda: mock_db
        try:
            response = await async_client.get(
                "/api/v1/admin/panel/acciones-por-dia",
                headers={"Authorization": "Bearer invalid-token"},
            )
            assert response.status_code in (401, 403)
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_max_param_enforced_to_1000(self, async_client: AsyncClient):
        from app.main import app
        user = MockUser()
        mock_db = _make_mock_db()
        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[_resolve_panel_permission] = lambda: (True, None)
        try:
            response = await async_client.get(
                "/api/v1/admin/panel/ultimas-acciones?max=5000",
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 422  # FastAPI max validation
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_router_registered_in_app(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert "/api/v1/admin/panel/acciones-por-dia" in routes
        assert "/api/v1/admin/panel/ultimas-acciones" in routes
        assert "/api/v1/admin/panel/comunicaciones-por-docente" in routes
        assert "/api/v1/admin/panel/interacciones-por-docente-materia" in routes
