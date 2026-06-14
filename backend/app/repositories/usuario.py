import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt, is_encrypted
from app.models.user import User
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[User]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(User, tenant_id)

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        result = await session.execute(
            select(User).where(
                User.tenant_id == self._tenant_id,
                User.deleted_at.is_(None),
            )
        )
        users = result.unique().scalars().all()
        for user in users:
            if is_encrypted(user.email):
                try:
                    decrypted = decrypt(user.email)
                except Exception:
                    continue
                if decrypted == email:
                    return user
            elif user.email == email:
                return user
        return None
