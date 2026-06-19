from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Request

from app.core.permissions import _match_permission, _parse_perm_codigo, require_permission
from app.models.user import User


class TestParsePermCodigo:
    def test_parse_simple(self):
        mod, acc, propio = _parse_perm_codigo("equipos:asignar")
        assert mod == "equipos"
        assert acc == "asignar"
        assert propio is False

    def test_parse_wildcard(self):
        mod, acc, propio = _parse_perm_codigo("liquidaciones:*")
        assert mod == "liquidaciones"
        assert acc == "*"
        assert propio is False

    def test_parse_propio(self):
        mod, acc, propio = _parse_perm_codigo("atrasados:ver(propio)")
        assert mod == "atrasados"
        assert acc == "ver"
        assert propio is True

    def test_parse_wildcard_propio(self):
        mod, acc, propio = _parse_perm_codigo("tareas:*(propio)")
        assert mod == "tareas"
        assert acc == "*"
        assert propio is True

    def test_parse_global_wildcard(self):
        mod, acc, propio = _parse_perm_codigo("*:*")
        assert mod == "*"
        assert acc == "*"
        assert propio is False


class TestMatchPermissionExact:
    def test_exact_match_passes(self):
        assert _match_permission("equipos:asignar", "equipos:asignar") is True

    def test_exact_no_match(self):
        assert _match_permission("equipos:asignar", "equipos:ver") is False

    def test_different_module_no_match(self):
        assert _match_permission("equipos:asignar", "liquidaciones:ver") is False


class TestMatchPermissionWildcard:
    def test_wildcard_action_matches_all(self):
        assert _match_permission("liquidaciones:ver", "liquidaciones:*") is True

    def test_wildcard_action_matches_any(self):
        assert _match_permission("liquidaciones:editar", "liquidaciones:*") is True

    def test_wildcard_module_matches_all(self):
        assert _match_permission("equipos:ver", "*:ver") is True

    def test_wildcard_both_matches(self):
        assert _match_permission("cualquier:cosa", "*:*") is True

    def test_wildcard_does_not_match_different_module(self):
        assert _match_permission("equipos:ver", "liquidaciones:*") is False


class TestMatchPermissionPropio:
    def test_global_can_access_propio(self):
        assert _match_permission("encuentros:ver(propio)", "encuentros:*") is True

    def test_propio_cannot_access_global(self):
        assert _match_permission("encuentros:ver", "encuentros:ver(propio)") is False

    def test_propio_matches_propio(self):
        assert _match_permission("encuentros:ver(propio)", "encuentros:ver(propio)") is True

    def test_global_all_wildcard_can_access_propio(self):
        assert _match_permission("perfil:ver(propio)", "*:*") is True

    def test_propio_wildcard_action(self):
        assert _match_permission("tareas:crear(propio)", "tareas:*(propio)") is True

    def test_propio_wildcard_does_not_match_global(self):
        assert _match_permission("tareas:crear", "tareas:*(propio)") is False


class TestMatchPermissionRoleUnion:
    def test_one_role_grants_permission(self):
        user_perms = ["equipos:asignar", "liquidaciones:ver"]
        assert _match_permission("equipos:asignar", user_perms[0]) is True

    def test_multiple_perms_one_matches(self):
        user_perms = ["equipos:ver", "liquidaciones:*"]
        assert any(_match_permission("liquidaciones:ver", p) for p in user_perms)


class TestRequirePermissionDependency:

    def test_factory_returns_callable(self):
        dep = require_permission("equipos:asignar")
        assert callable(dep)

    def test_factory_with_own_resource_check(self):
        async def check_owner(req, user):
            return True

        dep = require_permission("equipos:asignar", own_resource_check=check_owner)
        assert callable(dep)

    def test_factory_accepts_sync_callable(self):
        def check_owner(req, user):
            return True

        dep = require_permission("equipos:asignar", own_resource_check=check_owner)
        assert callable(dep)

    def test_factory_with_propio_perm(self):
        dep = require_permission("atrasados:ver(propio)")
        assert callable(dep)


class TestRequirePermissionDependencyExecution:
    """La dependencia devuelve is_propio para que el router sepa con qué scope se resolvió el permiso."""

    @staticmethod
    def _fake_request() -> MagicMock:
        request = MagicMock(spec=Request)
        request.headers = {"Authorization": "Bearer faketoken"}
        return request

    @pytest.mark.asyncio
    async def test_devuelve_true_cuando_el_grant_es_propio(self):
        dep = require_permission("tareas:gestionar(propio)")
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["PROFESOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, True))
            result = await dep(self._fake_request(), db=MagicMock(), current_user=MagicMock(spec=User))
            assert result is True

    @pytest.mark.asyncio
    async def test_devuelve_false_cuando_el_grant_es_full(self):
        dep = require_permission("tareas:gestionar")
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            result = await dep(self._fake_request(), db=MagicMock(), current_user=MagicMock(spec=User))
            assert result is False

    @pytest.mark.asyncio
    async def test_403_sin_permiso(self):
        dep = require_permission("tareas:gestionar")
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))
            with pytest.raises(HTTPException) as exc_info:
                await dep(self._fake_request(), db=MagicMock(), current_user=MagicMock(spec=User))
            assert exc_info.value.status_code == 403
