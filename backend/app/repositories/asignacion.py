import uuid

from app.models.asignacion import Asignacion
from app.repositories.base import BaseRepository


class AsignacionRepository(BaseRepository[Asignacion]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Asignacion, tenant_id)
