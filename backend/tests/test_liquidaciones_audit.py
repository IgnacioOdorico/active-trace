from app.services.audit_service import (
    LIQUIDACION_CALCULAR,
    LIQUIDACION_CERRAR,
    FACTURA_CARGAR,
    FACTURA_ABONAR,
    SALARIO_CONFIGURAR,
    AuditLogService,
)


class TestAuditActionsExist:
    def test_liquidacion_calcular_exists(self):
        assert LIQUIDACION_CALCULAR == "LIQUIDACION_CALCULAR"

    def test_liquidacion_cerrar_exists(self):
        assert LIQUIDACION_CERRAR == "LIQUIDACION_CERRAR"

    def test_factura_cargar_exists(self):
        assert FACTURA_CARGAR == "FACTURA_CARGAR"

    def test_factura_abonar_exists(self):
        assert FACTURA_ABONAR == "FACTURA_ABONAR"

    def test_salario_configurar_exists(self):
        assert SALARIO_CONFIGURAR == "SALARIO_CONFIGURAR"

    def test_audit_service_has_all_constants(self):
        svc = AuditLogService(tenant_id="00000000-0000-0000-0000-000000000000")
        assert svc.LIQUIDACION_CALCULAR == "LIQUIDACION_CALCULAR"
        assert svc.LIQUIDACION_CERRAR == "LIQUIDACION_CERRAR"
        assert svc.FACTURA_CARGAR == "FACTURA_CARGAR"
        assert svc.FACTURA_ABONAR == "FACTURA_ABONAR"
        assert svc.SALARIO_CONFIGURAR == "SALARIO_CONFIGURAR"
