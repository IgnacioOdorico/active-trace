import uuid


class DomainError(Exception):
    def __init__(self, detail: str, context: dict | None = None) -> None:
        self.detail = detail
        self.context = context or {}
        super().__init__(self.detail)


class TenantNotFoundError(DomainError):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(
            detail="Tenant not found",
            context={"tenant_id": str(tenant_id)},
        )


class EntityNotFoundError(DomainError):
    def __init__(self, entity_type: str, entity_id: uuid.UUID) -> None:
        super().__init__(
            detail=f"{entity_type} with id {entity_id} not found",
            context={"entity_type": entity_type, "entity_id": str(entity_id)},
        )


class EncryptionError(DomainError):
    def __init__(self, message: str = "Encryption operation failed") -> None:
        super().__init__(detail=message, context={})
