import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError, EntityNotFoundError
from app.core.security import decrypt, encrypt
from app.models.user import User
from app.repositories.usuario import UsuarioRepository
from app.schemas.usuarios import UsuarioCreate, UsuarioUpdate

_PII_FIELDS = {"email", "dni", "cuil", "cbu", "alias_cbu"}


class UsuarioService:
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

    async def create(self, db: AsyncSession, data: UsuarioCreate) -> User:
        existing = await self._repo.get_by_email(db, data.email)
        if existing is not None:
            raise DomainError("EMAIL_DUPLICADO", {"email": "email"})

        create_data = data.model_dump()
        password = create_data.pop("password", None)

        self._encrypt_pii(create_data)

        if password:
            from app.core.auth import hash_password

            create_data["hashed_password"] = hash_password(password)

        if "estado" in create_data:
            create_data["is_active"] = create_data["estado"] == "Activo"

        user = await self._repo.create(db, create_data)
        self._decrypt_pii(user)
        return user

    async def get(self, db: AsyncSession, id: uuid.UUID) -> User:
        user = await self._repo.get(db, id)
        if user is None:
            raise EntityNotFoundError(entity_type="User", entity_id=id)
        self._decrypt_pii(user)
        return user

    async def get_all(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        estado: str | None = None,
    ) -> tuple[list[User], int]:
        filters = {}
        if estado is not None:
            filters["estado"] = estado

        total = await self._repo.count(db, **filters)
        users = list(await self._repo.get_all(db, **filters))

        start = (page - 1) * page_size
        end = start + page_size
        page_users = users[start:end]

        for u in page_users:
            self._decrypt_pii(u)
        return page_users, total

    async def update(
        self, db: AsyncSession, id: uuid.UUID, data: UsuarioUpdate
    ) -> User:
        user = await self._repo.get(db, id)
        if user is None:
            raise EntityNotFoundError(entity_type="User", entity_id=id)

        update_data = data.model_dump(exclude_unset=True)

        password = update_data.pop("password", None)
        if password:
            from app.core.auth import hash_password

            update_data["hashed_password"] = hash_password(password)

        self._encrypt_pii(update_data)

        if "estado" in update_data:
            update_data["is_active"] = update_data["estado"] == "Activo"

        if "email" in update_data:
            existing = await self._repo.get_by_email(db, data.email)
            if existing is not None and existing.id != id:
                raise DomainError("EMAIL_DUPLICADO", {"email": "email"})

        user = await self._repo.update(db, id, update_data)
        self._decrypt_pii(user)
        return user

    async def soft_delete(self, db: AsyncSession, id: uuid.UUID) -> None:
        await self._repo.soft_delete(db, id)
