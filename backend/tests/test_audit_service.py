import uuid
from datetime import datetime

import pytest

from app.services.audit_service import (
    AuditLogService,
    CALIFICACIONES_IMPORTAR,
    PADRON_CARGAR,
    COMUNICACION_ENVIAR,
    ASIGNACION_MODIFICAR,
    LIQUIDACION_CERRAR,
    IMPERSONACION_INICIAR,
    IMPERSONACION_FINALIZAR,
    log_action,
    audit_log,
)


class TestActionCodeConstants:
    def test_calificaciones_importar(self):
        assert CALIFICACIONES_IMPORTAR == "CALIFICACIONES_IMPORTAR"

    def test_padron_cargar(self):
        assert PADRON_CARGAR == "PADRON_CARGAR"

    def test_comunicacion_enviar(self):
        assert COMUNICACION_ENVIAR == "COMUNICACION_ENVIAR"

    def test_asignacion_modificar(self):
        assert ASIGNACION_MODIFICAR == "ASIGNACION_MODIFICAR"

    def test_liquidacion_cerrar(self):
        assert LIQUIDACION_CERRAR == "LIQUIDACION_CERRAR"

    def test_impersonacion_iniciar(self):
        assert IMPERSONACION_INICIAR == "IMPERSONACION_INICIAR"

    def test_impersonacion_finalizar(self):
        assert IMPERSONACION_FINALIZAR == "IMPERSONACION_FINALIZAR"


class TestAuditLogService:
    def test_instantiate_with_tenant_id(self):
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert svc is not None

    def test_has_log_method(self):
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert hasattr(svc, "log")
        assert callable(svc.log)

    def test_has_list_method(self):
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert hasattr(svc, "list")
        assert callable(svc.list)

    def test_no_update_method(self):
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert not hasattr(svc, "update")

    def test_no_delete_method(self):
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert not hasattr(svc, "delete")

    def test_no_soft_delete_method(self):
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert not hasattr(svc, "soft_delete")

    def test_has_action_code_constants(self):
        svc = AuditLogService(tenant_id=uuid.uuid4())
        assert svc.CALIFICACIONES_IMPORTAR == "CALIFICACIONES_IMPORTAR"
        assert svc.PADRON_CARGAR == "PADRON_CARGAR"
        assert svc.IMPERSONACION_INICIAR == "IMPERSONACION_INICIAR"
        assert svc.IMPERSONACION_FINALIZAR == "IMPERSONACION_FINALIZAR"


class TestLogActionFunction:
    def test_log_action_is_callable(self):
        assert callable(log_action)


class TestAuditLogDecorator:
    def test_audit_log_is_decorator(self):
        assert callable(audit_log)
        decorated = audit_log(accion="TEST")
        assert callable(decorated)

    def test_audit_log_decorator_preserves_func_name(self):
        @audit_log(accion="TEST")
        async def my_handler():
            return "ok"

        assert my_handler.__name__ == "my_handler"

    def test_audit_log_decorator_is_async(self):
        import asyncio

        @audit_log(accion="TEST")
        async def my_handler():
            return "ok"

        result = asyncio.run(my_handler())
        assert result == "ok"


class TestAllActionCodesService:
    def test_all_codes_match_module_level(self):
        from app.services.audit_service import (
            AuditLogService as Svc,
            CALIFICACIONES_IMPORTAR as CI,
            PADRON_CARGAR as PC,
            COMUNICACION_ENVIAR as CE,
            ASIGNACION_MODIFICAR as AM,
            LIQUIDACION_CERRAR as LC,
            IMPERSONACION_INICIAR as II,
            IMPERSONACION_FINALIZAR as IF,
        )
        assert Svc.CALIFICACIONES_IMPORTAR == CI
        assert Svc.PADRON_CARGAR == PC
        assert Svc.COMUNICACION_ENVIAR == CE
        assert Svc.ASIGNACION_MODIFICAR == AM
        assert Svc.LIQUIDACION_CERRAR == LC
        assert Svc.IMPERSONACION_INICIAR == II
        assert Svc.IMPERSONACION_FINALIZAR == IF
