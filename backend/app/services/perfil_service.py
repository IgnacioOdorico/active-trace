import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.core.security import decrypt, encrypt
from app.models.user import User
from app.repositories.usuario import UsuarioRepository
from app.schemas.perfil import PerfilResponse, PerfilUpdate

_PII_FIELDS = {"email", "dni", "cuil", "cbu", "alias_cbu"}


class PerfilService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._repo = UsuarioRepository(tenant_id)

    def _encrypt_pii(self, data: dict) -> dict:
        for field in _PII_FIELDS:
            value = data.get(field)
            if value is not None:
                data[field] = encrypt(value)
        return data

    def _decrypt_pii(self, user: User) -> None:
        for field in _PII_FIELDS:
            value = getattr(user, field, None)
            if value is not None:
                try:
                    setattr(user, field, decrypt(value))
                except Exception:
                    pass

    def _to_response(self, user: User) -> PerfilResponse:
        return PerfilResponse(
            id=str(user.id),
            tenant_id=str(user.tenant_id),
            email=user.email,
            nombre=user.nombre,
            apellidos=user.apellidos,
            dni=user.dni,
            cuil=user.cuil,
            cbu=user.cbu,
            alias_cbu=user.alias_cbu,
            banco=user.banco,
            regional=user.regional,
            legajo=user.legajo,
            legajo_profesional=user.legajo_profesional,
            facturador=user.facturador,
            estado=user.estado,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def obtener(self, db: AsyncSession, user: User) -> PerfilResponse:
        self._decrypt_pii(user)
        return self._to_response(user)

    async def actualizar(
        self, db: AsyncSession, user: User, data: PerfilUpdate
    ) -> PerfilResponse:
        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data:
            existing = await self._repo.get_by_email(db, update_data["email"])
            if existing is not None and existing.id != user.id:
                raise DomainError("EMAIL_DUPLICADO", {"email": "email"})

        self._encrypt_pii(update_data)
        user = await self._repo.update(db, user.id, update_data)
        self._decrypt_pii(user)
        return self._to_response(user)
