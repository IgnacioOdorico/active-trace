from datetime import datetime

from app.schemas.audit import AuditLogFilter, AuditLogResponse, PaginatedAuditLogResponse


class TestAuditLogResponse:
    def test_all_fields_present(self):
        now = datetime.now()
        data = AuditLogResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            fecha_hora=now,
            actor_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            impersonado_id="ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj",
            materia_id="kkkkkkkk-llll-mmmm-nnnn-oooooooooooo",
            accion="TEST_ACCION",
            detalle={"key": "value"},
            filas_afectadas=42,
            ip="192.168.1.1",
            user_agent="test-agent",
        )
        assert data.id == "123e4567-e89b-12d3-a456-426614174000"
        assert data.fecha_hora == now
        assert data.actor_id == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        assert data.impersonado_id == "ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj"
        assert data.materia_id == "kkkkkkkk-llll-mmmm-nnnn-oooooooooooo"
        assert data.accion == "TEST_ACCION"
        assert data.detalle == {"key": "value"}
        assert data.filas_afectadas == 42
        assert data.ip == "192.168.1.1"
        assert data.user_agent == "test-agent"

    def test_optional_fields_none(self):
        now = datetime.now()
        data = AuditLogResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            fecha_hora=now,
            actor_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            accion="TEST_ACCION",
            filas_afectadas=0,
        )
        assert data.impersonado_id is None
        assert data.materia_id is None
        assert data.detalle is None
        assert data.ip is None
        assert data.user_agent is None

    def test_id_is_str(self):
        now = datetime.now()
        data = AuditLogResponse(
            id="some-uuid",
            fecha_hora=now,
            actor_id="actor-uuid",
            accion="TEST",
            filas_afectadas=0,
        )
        assert isinstance(data.id, str)
        assert isinstance(data.actor_id, str)


class TestAuditLogFilter:
    def test_all_fields_optional(self):
        f = AuditLogFilter()
        assert f.actor_id is None
        assert f.materia_id is None
        assert f.accion is None
        assert f.desde is None
        assert f.hasta is None
        assert f.pagina == 1
        assert f.por_pagina == 50

    def test_custom_values(self):
        desde = datetime(2026, 1, 1)
        hasta = datetime(2026, 6, 30)
        f = AuditLogFilter(
            actor_id="actor-uuid",
            materia_id="materia-uuid",
            accion="TEST_ACCION",
            desde=desde,
            hasta=hasta,
            pagina=2,
            por_pagina=10,
        )
        assert f.actor_id == "actor-uuid"
        assert f.materia_id == "materia-uuid"
        assert f.accion == "TEST_ACCION"
        assert f.desde == desde
        assert f.hasta == hasta
        assert f.pagina == 2
        assert f.por_pagina == 10


class TestPaginatedAuditLogResponse:
    def test_all_fields(self):
        now = datetime.now()
        item = AuditLogResponse(
            id="id-1",
            fecha_hora=now,
            actor_id="actor-1",
            accion="TEST",
            filas_afectadas=0,
        )
        resp = PaginatedAuditLogResponse(
            items=[item],
            total=1,
            pagina=1,
            por_pagina=50,
            total_paginas=1,
        )
        assert len(resp.items) == 1
        assert resp.total == 1
        assert resp.pagina == 1
        assert resp.por_pagina == 50
        assert resp.total_paginas == 1

    def test_empty_items(self):
        resp = PaginatedAuditLogResponse(
            items=[],
            total=0,
            pagina=1,
            por_pagina=50,
            total_paginas=0,
        )
        assert resp.items == []
        assert resp.total == 0
