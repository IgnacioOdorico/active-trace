import uuid

from pydantic import BaseModel


class LiquidacionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    cohorte_id: uuid.UUID
    periodo: str
    usuario_id: uuid.UUID
    docente_nombre: str
    rol: str
    comisiones: list[str] | None
    monto_base: float
    monto_plus: float
    total: float
    es_nexo: bool
    excluido_por_factura: bool
    estado: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class LiquidacionListResponse(BaseModel):
    items: list[LiquidacionResponse]
    total: int


class LiquidacionHistorialItem(BaseModel):
    id: str
    periodo: str
    cohorte_id: uuid.UUID
    estado: str
    total_docentes: int
    monto_total: float


class LiquidacionHistorialResponse(BaseModel):
    items: list[LiquidacionHistorialItem]
    total: int


class LiquidacionKPI(BaseModel):
    total_general: float
    total_nexo: float
    total_facturas_pendientes: float
    total_facturas_abonadas: float
    cantidad_docentes_general: int
    cantidad_docentes_nexo: int
    cantidad_docentes_facturantes: int


class CalcularLiquidacionRequest(BaseModel):
    cohorte_id: uuid.UUID
    periodo: str
