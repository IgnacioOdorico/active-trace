from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_access_token
from app.core.dependencies import get_current_user, get_db
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.user import User


def _parse_perm_codigo(codigo: str) -> tuple[str, str, bool]:
    modulo, accion = codigo.split(":", 1)
    is_propio = "(propio)" in accion
    accion = accion.replace("(propio)", "")
    return modulo, accion, is_propio


def _match_permission(required: str, user_perm: str) -> bool:
    req_mod, req_acc, req_propio = _parse_perm_codigo(required)
    usr_mod, usr_acc, usr_propio = _parse_perm_codigo(user_perm)

    if usr_mod != "*" and usr_mod != req_mod:
        return False

    if usr_acc != "*" and usr_acc != req_acc:
        return False

    if usr_propio and not req_propio:
        return False

    return True


class PermissionChecker:
    def __init__(self, role_cods: list[str], db: AsyncSession) -> None:
        self._role_cods = role_cods
        self._db = db
        self._cached_perms: list[str] | None = None

    async def _load_permissions(self) -> list[str]:
        if self._cached_perms is None:
            result = await self._db.execute(
                select(Permiso.codigo)
                .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
                .join(Rol, Rol.id == RolPermiso.rol_id)
                .where(Rol.codigo.in_(self._role_cods), Rol.activo == True)
            )
            self._cached_perms = list(result.scalars().all())
        return self._cached_perms

    async def has_permission(self, codigo: str) -> tuple[bool, bool]:
        perms = await self._load_permissions()
        for p in perms:
            if _match_permission(codigo, p):
                return True, _parse_perm_codigo(p)[2]
        return False, False


def require_permission(
    perm_codigo: str,
    own_resource_check: Callable[[Request, User], bool | Awaitable[bool]] | None = None,
) -> Any:
    async def _dependency(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> bool:
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        token = auth.split(" ", 1)[1]
        payload = decode_access_token(token)
        roles: list[str] = payload.get("rols", [])

        if not roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        checker = PermissionChecker(roles, db)
        has_perm, is_propio = await checker.has_permission(perm_codigo)
        if not has_perm:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        if is_propio and own_resource_check is not None:
            result = own_resource_check(request, current_user)
            if isinstance(result, bool):
                ok = result
            else:
                ok = await result
            if not ok:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your resource")

        return is_propio

    return _dependency
