import uuid

from app.models.factura import Factura
from app.models.liquidacion import Liquidacion
from app.models.salario_base import SalarioBase
from app.models.salario_plus import SalarioPlus


class TestSalarioBaseModel:
    def test_tablename(self):
        assert SalarioBase.__tablename__ == "salarios_base"

    def test_has_id(self):
        assert hasattr(SalarioBase, "id")

    def test_has_tenant_id(self):
        assert hasattr(SalarioBase, "tenant_id")

    def test_has_rol(self):
        assert hasattr(SalarioBase, "rol")

    def test_has_monto(self):
        assert hasattr(SalarioBase, "monto")

    def test_has_desde(self):
        assert hasattr(SalarioBase, "desde")

    def test_has_hasta(self):
        assert hasattr(SalarioBase, "hasta")

    def test_has_deleted_at(self):
        assert hasattr(SalarioBase, "deleted_at")

    def test_has_created_at(self):
        assert hasattr(SalarioBase, "created_at")

    def test_has_updated_at(self):
        assert hasattr(SalarioBase, "updated_at")


class TestSalarioPlusModel:
    def test_tablename(self):
        assert SalarioPlus.__tablename__ == "salarios_plus"

    def test_has_id(self):
        assert hasattr(SalarioPlus, "id")

    def test_has_tenant_id(self):
        assert hasattr(SalarioPlus, "tenant_id")

    def test_has_grupo(self):
        assert hasattr(SalarioPlus, "grupo")

    def test_has_rol(self):
        assert hasattr(SalarioPlus, "rol")

    def test_has_descripcion(self):
        assert hasattr(SalarioPlus, "descripcion")

    def test_has_monto(self):
        assert hasattr(SalarioPlus, "monto")

    def test_has_desde(self):
        assert hasattr(SalarioPlus, "desde")

    def test_has_hasta(self):
        assert hasattr(SalarioPlus, "hasta")

    def test_has_deleted_at(self):
        assert hasattr(SalarioPlus, "deleted_at")


class TestLiquidacionModel:
    def test_tablename(self):
        assert Liquidacion.__tablename__ == "liquidaciones"

    def test_has_id(self):
        assert hasattr(Liquidacion, "id")

    def test_has_tenant_id(self):
        assert hasattr(Liquidacion, "tenant_id")

    def test_has_cohorte_id(self):
        assert hasattr(Liquidacion, "cohorte_id")

    def test_has_periodo(self):
        assert hasattr(Liquidacion, "periodo")

    def test_has_usuario_id(self):
        assert hasattr(Liquidacion, "usuario_id")

    def test_has_rol(self):
        assert hasattr(Liquidacion, "rol")

    def test_has_comisiones(self):
        assert hasattr(Liquidacion, "comisiones")

    def test_has_monto_base(self):
        assert hasattr(Liquidacion, "monto_base")

    def test_has_monto_plus(self):
        assert hasattr(Liquidacion, "monto_plus")

    def test_has_total(self):
        assert hasattr(Liquidacion, "total")

    def test_has_es_nexo(self):
        assert hasattr(Liquidacion, "es_nexo")

    def test_has_excluido_por_factura(self):
        assert hasattr(Liquidacion, "excluido_por_factura")

    def test_has_estado(self):
        assert hasattr(Liquidacion, "estado")

    def test_has_created_at(self):
        assert hasattr(Liquidacion, "created_at")

    def test_has_updated_at(self):
        assert hasattr(Liquidacion, "updated_at")

    def test_has_deleted_at(self):
        """A diferencia de Factura, Liquidacion sí soporta soft-delete:
        recalcular un período 'Abierta' reemplaza el borrador (ver
        LiquidacionRepository.soft_delete_abiertas)."""
        assert hasattr(Liquidacion, "deleted_at")


class TestFacturaModel:
    def test_tablename(self):
        assert Factura.__tablename__ == "facturas"

    def test_has_id(self):
        assert hasattr(Factura, "id")

    def test_has_tenant_id(self):
        assert hasattr(Factura, "tenant_id")

    def test_has_usuario_id(self):
        assert hasattr(Factura, "usuario_id")

    def test_has_periodo(self):
        assert hasattr(Factura, "periodo")

    def test_has_detalle(self):
        assert hasattr(Factura, "detalle")

    def test_has_referencia_archivo(self):
        assert hasattr(Factura, "referencia_archivo")

    def test_has_tamano_kb(self):
        assert hasattr(Factura, "tamano_kb")

    def test_has_estado(self):
        assert hasattr(Factura, "estado")

    def test_has_cargada_at(self):
        assert hasattr(Factura, "cargada_at")

    def test_has_abonada_at(self):
        assert hasattr(Factura, "abonada_at")

    def test_has_created_at(self):
        assert hasattr(Factura, "created_at")

    def test_has_updated_at(self):
        assert hasattr(Factura, "updated_at")

    def test_no_deleted_at(self):
        assert not hasattr(Factura, "deleted_at")
