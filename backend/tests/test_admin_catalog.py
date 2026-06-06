"""Admin catalog endpoint tests (structure only, no DB)."""

from app.api.v1.routers.admin import router


class TestAdminRouter:
    def test_router_prefix(self):
        assert router.prefix == "/api/v1/admin"

    def test_router_has_routes(self):
        assert len(router.routes) >= 8

    def test_router_has_list_roles(self):
        route_names = {r.name for r in router.routes if r.name}
        assert "list_roles" in route_names

    def test_router_has_create_role(self):
        route_names = {r.name for r in router.routes if r.name}
        assert "create_role" in route_names

    def test_router_has_update_role(self):
        route_names = {r.name for r in router.routes if r.name}
        assert "update_role" in route_names

    def test_router_has_delete_role(self):
        route_names = {r.name for r in router.routes if r.name}
        assert "delete_role" in route_names

    def test_router_has_list_permisos(self):
        route_names = {r.name for r in router.routes if r.name}
        assert "list_permisos" in route_names

    def test_router_has_create_permiso(self):
        route_names = {r.name for r in router.routes if r.name}
        assert "create_permiso" in route_names

    def test_router_has_list_role_permisos(self):
        route_names = {r.name for r in router.routes if r.name}
        assert "list_role_permisos" in route_names

    def test_router_has_assign_permiso(self):
        route_names = {r.name for r in router.routes if r.name}
        assert "assign_permiso" in route_names

    def test_router_has_remove_permiso(self):
        route_names = {r.name for r in router.routes if r.name}
        assert "remove_permiso" in route_names

    def test_get_roles_path(self):
        matching = [r for r in router.routes if hasattr(r, "path") and "/roles" in r.path]
        assert any("GET" in getattr(r, "methods", set()) for r in matching)
