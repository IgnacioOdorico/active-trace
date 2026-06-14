import uuid
from datetime import date, time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.exceptions import DomainError


class TestCalcularFechas:
    def test_calcula_fechas_semanales(self):
        from app.services.encuentro_service import EncuentroService
        fechas = EncuentroService._calcular_fechas(
            fecha_inicio=date(2026, 4, 1),
            dia_semana="Miércoles",
            cant_semanas=8,
        )
        assert len(fechas) == 8
        assert fechas[0] == date(2026, 4, 1)
        assert fechas[1] == date(2026, 4, 8)
        assert fechas[7] == date(2026, 5, 20)

    def test_valida_coincidencia_dia_semana(self):
        from app.services.encuentro_service import EncuentroService
        with pytest.raises(DomainError, match="no coincide"):
            EncuentroService._calcular_fechas(
                fecha_inicio=date(2026, 4, 1),
                dia_semana="Lunes",
                cant_semanas=8,
            )

    def test_rechaza_mas_de_52_semanas(self):
        from app.services.encuentro_service import EncuentroService
        with pytest.raises(DomainError, match="máximo"):
            EncuentroService._calcular_fechas(
                fecha_inicio=date(2026, 4, 1),
                dia_semana="Miércoles",
                cant_semanas=53,
            )

    def test_cant_semanas_1_genera_una_fecha(self):
        from app.services.encuentro_service import EncuentroService
        fechas = EncuentroService._calcular_fechas(
            fecha_inicio=date(2026, 4, 1),
            dia_semana="Miércoles",
            cant_semanas=1,
        )
        assert len(fechas) == 1
        assert fechas[0] == date(2026, 4, 1)


class TestTransicionesEncuentro:
    def test_programado_a_realizado_valida(self):
        from app.services.encuentro_service import EncuentroService
        EncuentroService._validar_transicion_estado("Programado", "Realizado")

    def test_programado_a_cancelado_valida(self):
        from app.services.encuentro_service import EncuentroService
        EncuentroService._validar_transicion_estado("Programado", "Cancelado")

    def test_cancelado_a_realizado_invalida(self):
        from app.services.encuentro_service import EncuentroService
        with pytest.raises(DomainError, match="Transición inválida"):
            EncuentroService._validar_transicion_estado("Cancelado", "Realizado")

    def test_realizado_a_cancelado_invalida(self):
        from app.services.encuentro_service import EncuentroService
        with pytest.raises(DomainError, match="Transición inválida"):
            EncuentroService._validar_transicion_estado("Realizado", "Cancelado")

    def test_mismo_estado_no_hay_transicion(self):
        from app.services.encuentro_service import EncuentroService
        EncuentroService._validar_transicion_estado("Programado", "Programado")


class TestEncuentroServiceCrearSlot:
    @pytest.mark.asyncio
    async def test_crear_slot_recurrente_ok(self):
        from app.services.encuentro_service import EncuentroService

        tenant_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._slot_repo = AsyncMock()
        svc._instancia_repo = AsyncMock()
        svc._audit_service = AsyncMock()
        svc._audit_service.log = AsyncMock()

        mock_slot = Mock()
        mock_slot.id = uuid.uuid4()

        svc._slot_repo.create = AsyncMock(return_value=mock_slot)
        svc._instancia_repo.create = AsyncMock()

        data = {
            "materia_id": materia_id,
            "titulo": "Clase 1",
            "hora": time(14, 0),
            "dia_semana": "Miércoles",
            "fecha_inicio": date(2026, 4, 1),
            "cant_semanas": 8,
            "meet_url": "https://meet.google.com/abc",
            "vig_desde": date(2026, 4, 1),
        }

        result = await svc.crear_slot_recurrente(data, usuario_id, AsyncMock())

        assert result is not None
        assert svc._slot_repo.create.call_count == 1
        assert svc._instancia_repo.create.call_count == 8
        svc._audit_service.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_crear_slot_recurrente_genera_audit(self):
        from app.services.encuentro_service import EncuentroService
        from app.services.audit_service import AuditLogService

        tenant_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._slot_repo = AsyncMock()
        svc._instancia_repo = AsyncMock()
        svc._audit_service = AsyncMock()
        svc._audit_service.log = AsyncMock()

        mock_slot = Mock()
        mock_slot.id = uuid.uuid4()
        svc._slot_repo.create = AsyncMock(return_value=mock_slot)
        svc._instancia_repo.create = AsyncMock()

        data = {
            "materia_id": materia_id,
            "titulo": "Clase 1",
            "hora": time(14, 0),
            "dia_semana": "Miércoles",
            "fecha_inicio": date(2026, 4, 1),
            "cant_semanas": 3,
            "meet_url": "https://meet.google.com/abc",
            "vig_desde": date(2026, 4, 1),
        }

        await svc.crear_slot_recurrente(data, usuario_id, AsyncMock())

        call_args = svc._audit_service.log.call_args
        assert call_args is not None
        kwargs = call_args[1]
        assert kwargs["accion"] == AuditLogService.ENCUENTRO_CREAR
        assert kwargs["actor_id"] == usuario_id
        assert kwargs["materia_id"] == materia_id


class TestEncuentroServiceCrearUnico:
    @pytest.mark.asyncio
    async def test_crear_encuentro_unico_ok(self):
        from app.services.encuentro_service import EncuentroService

        tenant_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._instancia_repo = AsyncMock()
        svc._audit_service = AsyncMock()
        svc._audit_service.log = AsyncMock()

        mock_instancia = Mock()
        mock_instancia.id = uuid.uuid4()
        mock_instancia.materia_id = materia_id
        svc._instancia_repo.create = AsyncMock(return_value=mock_instancia)

        data = {
            "materia_id": materia_id,
            "fecha": date(2026, 5, 1),
            "hora": time(10, 0),
            "titulo": "Clase única",
            "meet_url": "https://meet.google.com/xyz",
        }

        result = await svc.crear_encuentro_unico(data, usuario_id, AsyncMock())

        assert result is not None
        svc._instancia_repo.create.assert_called_once()
        svc._audit_service.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_crear_encuentro_unico_sin_meet_url(self):
        from app.services.encuentro_service import EncuentroService

        tenant_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._instancia_repo = AsyncMock()
        svc._audit_service = AsyncMock()

        mock_instancia = Mock()
        mock_instancia.id = uuid.uuid4()
        svc._instancia_repo.create = AsyncMock(return_value=mock_instancia)
        svc._audit_service.log = AsyncMock()

        data = {
            "materia_id": materia_id,
            "fecha": date(2026, 5, 1),
            "hora": time(10, 0),
            "titulo": "Clase única",
            "meet_url": "",
        }

        result = await svc.crear_encuentro_unico(data, usuario_id, AsyncMock())

        assert result is not None


class TestEncuentroServiceEditar:
    @pytest.mark.asyncio
    async def test_editar_instancia_programado_a_realizado(self):
        from app.services.encuentro_service import EncuentroService

        tenant_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        instancia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._instancia_repo = AsyncMock()
        svc._slot_repo = AsyncMock()
        svc._audit_service = AsyncMock()
        svc._audit_service.log = AsyncMock()

        mock_instancia = Mock()
        mock_instancia.id = instancia_id
        mock_instancia.estado = "Programado"
        svc._instancia_repo.get = AsyncMock(return_value=mock_instancia)
        svc._instancia_repo.update = AsyncMock(return_value=mock_instancia)

        data = {"estado": "Realizado", "video_url": "https://youtube.com/abc"}
        result = await svc.editar_instancia(instancia_id, data, usuario_id, AsyncMock())

        assert result is not None
        assert mock_instancia.estado == "Realizado"
        svc._audit_service.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_editar_instancia_cancelado_a_realizado_rechaza(self):
        from app.services.encuentro_service import EncuentroService

        tenant_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        instancia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._instancia_repo = AsyncMock()
        svc._slot_repo = AsyncMock()
        svc._audit_service = AsyncMock()

        mock_instancia = Mock()
        mock_instancia.id = instancia_id
        mock_instancia.estado = "Cancelado"
        svc._instancia_repo.get = AsyncMock(return_value=mock_instancia)

        data = {"estado": "Realizado"}
        with pytest.raises(DomainError, match="Transición inválida"):
            await svc.editar_instancia(instancia_id, data, usuario_id, AsyncMock())

    @pytest.mark.asyncio
    async def test_editar_instancia_no_existe(self):
        from app.services.encuentro_service import EncuentroService

        tenant_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        instancia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._instancia_repo = AsyncMock()
        svc._slot_repo = AsyncMock()
        svc._audit_service = AsyncMock()

        svc._instancia_repo.get = AsyncMock(return_value=None)

        data = {"estado": "Realizado"}
        with pytest.raises(DomainError, match="no encontrada"):
            await svc.editar_instancia(instancia_id, data, usuario_id, AsyncMock())


class TestEncuentroServiceGenerarHTML:
    @pytest.mark.asyncio
    async def test_generar_html_con_encuentros(self):
        from app.services.encuentro_service import EncuentroService

        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._instancia_repo = AsyncMock()

        mock_instancia = Mock()
        mock_instancia.fecha = date(2026, 4, 1)
        mock_instancia.hora = time(14, 0)
        mock_instancia.titulo = "Clase 1"
        mock_instancia.meet_url = "https://meet.google.com/abc"
        mock_instancia.estado = "Programado"
        mock_instancia.video_url = None

        svc._instancia_repo.get_by_materia_filtros = AsyncMock(return_value=[mock_instancia])

        result = await svc.generar_html(materia_id, AsyncMock())

        assert '<table class="encuentros">' in result["html"]
        assert "Clase 1" in result["html"]
        assert "meet.google.com" in result["html"]

    @pytest.mark.asyncio
    async def test_generar_html_sin_encuentros(self):
        from app.services.encuentro_service import EncuentroService

        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._instancia_repo = AsyncMock()
        svc._instancia_repo.get_by_materia_filtros = AsyncMock(return_value=[])

        result = await svc.generar_html(materia_id, AsyncMock())

        assert "No hay encuentros programados" in result["html"]
        assert "<p>" in result["html"]


class TestEncuentroServiceListar:
    @pytest.mark.asyncio
    async def test_listar_encuentros_paginados(self):
        from app.services.encuentro_service import EncuentroService

        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        svc = EncuentroService(tenant_id)
        svc._instancia_repo = AsyncMock()

        mock_instancia = Mock()
        mock_instancia.id = uuid.uuid4()
        mock_instancia.slot_id = None
        mock_instancia.materia_id = materia_id
        mock_instancia.fecha = date(2026, 4, 1)
        mock_instancia.hora = time(14, 0)
        mock_instancia.titulo = "Clase"
        mock_instancia.estado = "Programado"
        mock_instancia.meet_url = "https://meet.google.com/abc"
        mock_instancia.video_url = None
        mock_instancia.comentario = None

        svc._instancia_repo.get_by_materia_filtros = AsyncMock(
            return_value=[mock_instancia]
        )

        result = await svc.listar(
            {"materia_id": materia_id}, pagina=1, page_size=10, db=AsyncMock()
        )

        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["pagina"] == 1
        assert result["page_size"] == 10


class TestTransicionesGuardia:
    def test_pendiente_a_realizada_valida(self):
        from app.services.guardia_service import GuardiaService
        GuardiaService._validar_transicion_estado("Pendiente", "Realizada")

    def test_pendiente_a_cancelada_valida(self):
        from app.services.guardia_service import GuardiaService
        GuardiaService._validar_transicion_estado("Pendiente", "Cancelada")

    def test_cancelada_a_pendiente_invalida(self):
        from app.services.guardia_service import GuardiaService
        with pytest.raises(DomainError, match="Transición inválida"):
            GuardiaService._validar_transicion_estado("Cancelada", "Pendiente")


class TestGuardiaService:
    @pytest.mark.asyncio
    async def test_crear_guardia_ok(self):
        from app.services.guardia_service import GuardiaService

        tenant_id = uuid.uuid4()
        usuario_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        svc = GuardiaService(tenant_id)
        svc._guardia_repo = AsyncMock()
        svc._audit_service = AsyncMock()
        svc._audit_service.log = AsyncMock()

        mock_guardia = Mock()
        mock_guardia.id = uuid.uuid4()
        svc._guardia_repo.create = AsyncMock(return_value=mock_guardia)

        data = {
            "materia_id": materia_id,
            "carrera_id": uuid.uuid4(),
            "dia": "Lunes",
            "horario": "14:00–14:45",
        }

        result = await svc.crear(data, usuario_id, uuid.uuid4(), AsyncMock())

        assert result is not None
        svc._guardia_repo.create.assert_called_once()
        svc._audit_service.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_listar_mis_guardias(self):
        from app.services.guardia_service import GuardiaService

        tenant_id = uuid.uuid4()
        asignacion_id = uuid.uuid4()

        svc = GuardiaService(tenant_id)
        svc._guardia_repo = AsyncMock()

        mock_guardia = Mock()
        mock_guardia.id = uuid.uuid4()
        mock_guardia.asignacion_id = asignacion_id
        mock_guardia.materia_id = uuid.uuid4()
        mock_guardia.carrera_id = uuid.uuid4()
        mock_guardia.cohorte_id = None
        mock_guardia.dia = "Lunes"
        mock_guardia.horario = "14:00–14:45"
        mock_guardia.estado = "Pendiente"
        mock_guardia.comentarios = None

        svc._guardia_repo.get_by_asignacion = AsyncMock(return_value=[mock_guardia])

        result = await svc.listar_mis_guardias(asignacion_id, pagina=1, page_size=10, db=AsyncMock())

        assert result["total"] == 1
        assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_listar_todas(self):
        from app.services.guardia_service import GuardiaService

        tenant_id = uuid.uuid4()

        svc = GuardiaService(tenant_id)
        svc._guardia_repo = AsyncMock()
        svc._guardia_repo.get_all_filtros = AsyncMock(return_value=[])

        result = await svc.listar_todas({}, pagina=1, page_size=10, db=AsyncMock())

        assert result["total"] == 0
        assert result["items"] == []

    @pytest.mark.asyncio
    async def test_editar_guardia_ok(self):
        from app.services.guardia_service import GuardiaService

        tenant_id = uuid.uuid4()
        guardia_id = uuid.uuid4()

        svc = GuardiaService(tenant_id)
        svc._guardia_repo = AsyncMock()
        svc._audit_service = AsyncMock()

        mock_guardia = Mock()
        mock_guardia.id = guardia_id
        mock_guardia.estado = "Pendiente"
        svc._guardia_repo.get = AsyncMock(return_value=mock_guardia)
        svc._guardia_repo.update = AsyncMock(return_value=mock_guardia)

        result = await svc.editar(guardia_id, {"estado": "Realizada"}, AsyncMock())

        assert result is not None
        assert mock_guardia.estado == "Realizada"

    @pytest.mark.asyncio
    async def test_editar_guardia_no_existe(self):
        from app.services.guardia_service import GuardiaService

        tenant_id = uuid.uuid4()
        guardia_id = uuid.uuid4()

        svc = GuardiaService(tenant_id)
        svc._guardia_repo = AsyncMock()
        svc._audit_service = AsyncMock()
        svc._guardia_repo.get = AsyncMock(return_value=None)

        with pytest.raises(DomainError, match="no encontrada"):
            await svc.editar(guardia_id, {"estado": "Realizada"}, AsyncMock())

    @pytest.mark.asyncio
    async def test_exportar_guardias(self):
        from app.services.guardia_service import GuardiaService

        tenant_id = uuid.uuid4()

        svc = GuardiaService(tenant_id)
        svc._guardia_repo = AsyncMock()
        svc._guardia_repo.get_all_filtros = AsyncMock(return_value=[])

        result = await svc.exportar({}, AsyncMock())

        assert result["items"] == []
