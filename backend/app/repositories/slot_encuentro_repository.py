import uuid

from app.models.slot_encuentro import SlotEncuentro
from app.repositories.base import BaseRepository


class SlotEncuentroRepository(BaseRepository[SlotEncuentro]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(SlotEncuentro, tenant_id)
