import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.main import app
from app.models.user import User


class TestEstadoComunicacion:
    def test_enum_values(self):
        from app.models.comunicacion import EstadoComunicacion
        assert EstadoComunicacion.NUEVA.value == "Nueva"
        assert EstadoComunicacion.PENDIENTE_APROBACION.value == "PendienteAprobacion"
        assert EstadoComunicacion.PENDIENTE.value == "Pendiente"
        assert EstadoComunicacion.ENVIANDO.value == "Enviando"
        assert EstadoComunicacion.ENVIADO.value == "Enviado"
        assert EstadoComunicacion.ERROR.value == "Error"
        assert EstadoComunicacion.CANCELADO.value == "Cancelado"

    def test_enum_all_members_present(self):
        from app.models.comunicacion import EstadoComunicacion
        expected = {"Nueva", "PendienteAprobacion", "Pendiente", "Enviando", "Enviado", "Error", "Cancelado"}
        actual = {m.value for m in EstadoComunicacion}
        assert actual == expected


class TestComunicacionModel:
    def test_tablename(self):
        from app.models.comunicacion import Comunicacion
        assert Comunicacion.__tablename__ == "comunicacion"

    def test_has_fields(self):
        from app.models.comunicacion import Comunicacion
        assert hasattr(Comunicacion, "id")
        assert hasattr(Comunicacion, "tenant_id")
        assert hasattr(Comunicacion, "enviado_por")
        assert hasattr(Comunicacion, "materia_id")
        assert hasattr(Comunicacion, "destinatario")
        assert hasattr(Comunicacion, "asunto")
        assert hasattr(Comunicacion, "cuerpo")
        assert hasattr(Comunicacion, "lote_id")
        assert hasattr(Comunicacion, "intentos")
        assert hasattr(Comunicacion, "error_msg")
        assert hasattr(Comunicacion, "estado")
        assert hasattr(Comunicacion, "enviado_at")
        assert hasattr(Comunicacion, "enqueue_at")
        assert hasattr(Comunicacion, "created_at")
        assert hasattr(Comunicacion, "updated_at")
        assert hasattr(Comunicacion, "deleted_at")

    def test_enviado_por_fk(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["enviado_por"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "users"

    def test_materia_id_fk(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["materia_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "materias"

    def test_destinatario_string_500(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["destinatario"]
        assert col.type.length == 500
        assert col.nullable is False

    def test_asunto_string_200(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["asunto"]
        assert col.type.length == 200
        assert col.nullable is False

    def test_cuerpo_text(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["cuerpo"]
        assert col.nullable is False

    def test_lote_id_nullable(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["lote_id"]
        assert col.nullable is True

    def test_intentos_default_0(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["intentos"]
        assert col.nullable is False

    def test_estado_string_30(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["estado"]
        assert col.type.length == 30
        assert col.nullable is False

    def test_estado_default_nueva(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["estado"]
        assert col.default is not None

    def test_error_msg_nullable(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["error_msg"]
        assert col.nullable is True

    def test_enviado_at_nullable(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["enviado_at"]
        assert col.nullable is True

    def test_enqueue_at_nullable(self):
        from app.models.comunicacion import Comunicacion
        col = Comunicacion.__mapper__.columns["enqueue_at"]
        assert col.nullable is True


class TestTenantRequiereAprobacion:
    def test_has_requiere_aprobacion_field(self):
        from app.models.tenant import Tenant
        assert hasattr(Tenant, "requiere_aprobacion_comunicaciones")

    def test_field_is_boolean(self):
        from app.models.tenant import Tenant
        col = Tenant.__mapper__.columns["requiere_aprobacion_comunicaciones"]
        assert str(col.type).startswith("BOOL")
        assert col.nullable is False

    def test_field_default_false(self):
        from app.models.tenant import Tenant
        col = Tenant.__mapper__.columns["requiere_aprobacion_comunicaciones"]
        assert col.default is not None


class TestEstadoTransiciones:
    def test_transiciones_validas_contiene_todas(self):
        from app.services.comunicacion_service import ComunicacionService
        transiciones = ComunicacionService._transiciones_validas()
        expected = {
            frozenset({"Nueva", "Pendiente"}),
            frozenset({"Nueva", "PendienteAprobacion"}),
            frozenset({"PendienteAprobacion", "Pendiente"}),
            frozenset({"PendienteAprobacion", "Cancelado"}),
            frozenset({"Pendiente", "Cancelado"}),
            frozenset({"Pendiente", "Enviando"}),
            frozenset({"Enviando", "Enviado"}),
            frozenset({"Enviando", "Pendiente"}),
            frozenset({"Enviando", "Error"}),
        }
        actual = {frozenset({k, v}) for k, vals in transiciones.items() for v in vals}
        assert actual == expected

    def test_transicion_nueva_a_pendiente_valida(self):
        from app.services.comunicacion_service import ComunicacionService
        ComunicacionService._validar_transicion("Nueva", "Pendiente")

    def test_transicion_nueva_a_pendiente_aprobacion_valida(self):
        from app.services.comunicacion_service import ComunicacionService
        ComunicacionService._validar_transicion("Nueva", "PendienteAprobacion")

    def test_transicion_pendiente_aprobacion_a_pendiente_valida(self):
        from app.services.comunicacion_service import ComunicacionService
        ComunicacionService._validar_transicion("PendienteAprobacion", "Pendiente")

    def test_transicion_pendiente_aprobacion_a_cancelado_valida(self):
        from app.services.comunicacion_service import ComunicacionService
        ComunicacionService._validar_transicion("PendienteAprobacion", "Cancelado")

    def test_transicion_pendiente_a_enviando_valida(self):
        from app.services.comunicacion_service import ComunicacionService
        ComunicacionService._validar_transicion("Pendiente", "Enviando")

    def test_transicion_enviando_a_enviado_valida(self):
        from app.services.comunicacion_service import ComunicacionService
        ComunicacionService._validar_transicion("Enviando", "Enviado")

    def test_transicion_enviando_a_pendiente_valida(self):
        from app.services.comunicacion_service import ComunicacionService
        ComunicacionService._validar_transicion("Enviando", "Pendiente")

    def test_transicion_enviando_a_error_valida(self):
        from app.services.comunicacion_service import ComunicacionService
        ComunicacionService._validar_transicion("Enviando", "Error")

    def test_transicion_pendiente_a_cancelado_valida(self):
        from app.services.comunicacion_service import ComunicacionService
        ComunicacionService._validar_transicion("Pendiente", "Cancelado")

    def test_transicion_nueva_a_enviado_invalida(self):
        from app.services.comunicacion_service import ComunicacionService
        with pytest.raises(DomainError, match="Transición inválida"):
            ComunicacionService._validar_transicion("Nueva", "Enviado")

    def test_transicion_cancelado_a_pendiente_invalida(self):
        from app.services.comunicacion_service import ComunicacionService
        with pytest.raises(DomainError, match="Transición inválida"):
            ComunicacionService._validar_transicion("Cancelado", "Pendiente")

    def test_transicion_enviado_a_pendiente_invalida(self):
        from app.services.comunicacion_service import ComunicacionService
        with pytest.raises(DomainError, match="Transición inválida"):
            ComunicacionService._validar_transicion("Enviado", "Pendiente")

    def test_transicion_error_a_pendiente_invalida(self):
        from app.services.comunicacion_service import ComunicacionService
        with pytest.raises(DomainError, match="Transición inválida"):
            ComunicacionService._validar_transicion("Error", "Pendiente")


class TestComunicacionModelRegistered:
    def test_model_registered_in_init(self):
        from app.models import Comunicacion
        assert Comunicacion is not None

    def test_tenant_model_has_new_field(self):
        from app.models import Tenant
        assert hasattr(Tenant, "requiere_aprobacion_comunicaciones")


class _MockScalars:
    def __init__(self, values=None):
        self._values = values if values is not None else []

    def all(self):
        return self._values

    def first(self):
        return self._values[0] if self._values else None

    def one_or_none(self):
        return self._values[0] if self._values else None

    def one(self):
        if not self._values:
            raise ValueError("No result")
        return self._values[0]


class _MockUniqueResult:
    def __init__(self, values=None):
        self._values = values if values is not None else []
        self.scalar_one = Mock(return_value=3)

    def unique(self):
        return self

    def scalars(self):
        return _MockScalars(self._values)


class TestComunicacionRepository:
    @pytest.mark.asyncio
    async def test_get_pendientes_filters_by_estado(self):
        from app.repositories.comunicacion_repository import ComunicacionRepository
        tenant_id = uuid.uuid4()
        repo = ComunicacionRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        result = await repo.get_pendientes(mock_session, limit=10)

        assert result == []
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert "estado" in compiled
        assert "Pendiente" in compiled
        assert "ORDER BY" in compiled.upper()
        assert "created_at" in compiled

    @pytest.mark.asyncio
    async def test_get_pendientes_respects_limit(self):
        from app.repositories.comunicacion_repository import ComunicacionRepository
        tenant_id = uuid.uuid4()
        repo = ComunicacionRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        await repo.get_pendientes(mock_session, limit=50)

        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert "LIMIT" in compiled.upper()
        assert "50" in compiled

    @pytest.mark.asyncio
    async def test_get_by_lote(self):
        from app.repositories.comunicacion_repository import ComunicacionRepository
        tenant_id = uuid.uuid4()
        lote_id = uuid.uuid4()
        repo = ComunicacionRepository(tenant_id)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=_MockUniqueResult([]))

        result = await repo.get_by_lote(mock_session, lote_id)

        assert result == []
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert lote_id.hex in compiled

    @pytest.mark.asyncio
    async def test_batch_update_estado(self):
        from app.repositories.comunicacion_repository import ComunicacionRepository
        tenant_id = uuid.uuid4()
        lote_id = uuid.uuid4()
        repo = ComunicacionRepository(tenant_id)

        mock_execute = AsyncMock()
        mock_execute.rowcount = 5
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_execute)

        result = await repo.batch_update_estado(mock_session, lote_id, "PendienteAprobacion", "Cancelado")

        assert result == 5
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert "UPDATE" in compiled.upper()
        assert "Cancelado" in compiled
        assert lote_id.hex in compiled

    @pytest.mark.asyncio
    async def test_count_by_lote(self):
        from app.repositories.comunicacion_repository import ComunicacionRepository
        tenant_id = uuid.uuid4()
        lote_id = uuid.uuid4()
        repo = ComunicacionRepository(tenant_id)

        mock_result = _MockUniqueResult([])
        mock_result.scalar_one = Mock(return_value=3)
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.count_by_lote(mock_session, lote_id)

        assert result == 3
        call_query = mock_session.execute.call_args[0][0]
        compiled = str(call_query.compile(compile_kwargs={"literal_binds": True}))
        assert "COUNT" in compiled.upper()
        assert lote_id.hex in compiled


class _MockProveedor:
    def __init__(self, debe_fallar=False):
        self._debe_fallar = debe_fallar
        self.enviados = []

    async def enviar(self, destinatario, asunto, cuerpo):
        if self._debe_fallar:
            raise RuntimeError("Simulated error")
        self.enviados.append(destinatario)


class TestComunicacionServicePreview:
    @pytest.mark.asyncio
    async def test_preview_exitoso(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.VersionPadronRepository") as MockVR,
            patch("app.services.comunicacion_service.EntradaPadronRepository") as MockER,
        ):
            mock_version = AsyncMock()
            mock_version.id = uuid.uuid4()
            MockVR.return_value.get_active_by_materia = AsyncMock(return_value=[mock_version])

            mock_entrada = Mock()
            mock_entrada.nombre = "Juan"
            mock_entrada.apellidos = "Perez"
            mock_entrada.email = "juan@test.com"
            mock_entrada.comision = "A"
            MockER.return_value.get_by_version = AsyncMock(return_value=[mock_entrada])

            svc = ComunicacionService(tenant_id)
            result = await svc.preview(
                materia_id,
                "juan@test.com",
                "Hola $nombre",
                "Tu comision es $comision",
                AsyncMock(),
            )

            assert result["asunto"] == "Hola Juan"
            assert result["cuerpo"] == "Tu comision es A"

    @pytest.mark.asyncio
    async def test_preview_destinatario_no_encontrado(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.VersionPadronRepository") as MockVR,
            patch("app.services.comunicacion_service.EntradaPadronRepository") as MockER,
        ):
            mock_version = AsyncMock()
            mock_version.id = uuid.uuid4()
            MockVR.return_value.get_active_by_materia = AsyncMock(return_value=[mock_version])

            mock_entrada = Mock()
            mock_entrada.email = "otro@test.com"
            MockER.return_value.get_by_version = AsyncMock(return_value=[mock_entrada])

            svc = ComunicacionService(tenant_id)
            with pytest.raises(DomainError, match="Destinatario no encontrado"):
                await svc.preview(materia_id, "noexiste@test.com", "$nombre", "$cuerpo", AsyncMock())

    @pytest.mark.asyncio
    async def test_preview_sin_padron_activo(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()

        with patch("app.services.comunicacion_service.VersionPadronRepository") as MockVR:
            MockVR.return_value.get_active_by_materia = AsyncMock(return_value=[])

            svc = ComunicacionService(tenant_id)
            with pytest.raises(DomainError, match="No hay un padrón activo"):
                await svc.preview(materia_id, "a@b.com", "$nombre", "$cuerpo", AsyncMock())


class TestComunicacionServiceEnviar:
    @pytest.mark.asyncio
    async def test_enviar_sin_aprobacion_crea_pendientes(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.AuditLogService") as MockAudit,
            patch("app.services.comunicacion_service.encrypt") as mock_encrypt,
        ):
            mock_encrypt.side_effect = lambda e: f"[cifrado]{e}"
            MockCR.return_value.create = AsyncMock()
            mock_tenant = Mock()
            mock_tenant.requiere_aprobacion_comunicaciones = False

            svc = ComunicacionService(tenant_id)
            svc._get_tenant = AsyncMock(return_value=mock_tenant)
            MockAudit.return_value.log = AsyncMock()

            result = await svc.enviar(
                materia_id,
                ["a@test.com", "b@test.com"],
                "Asunto $nombre",
                "Cuerpo $nombre",
                usuario_id,
                AsyncMock(),
            )

            assert result["cantidad"] == 2
            assert result["estado"] == "Pendiente"
            assert MockCR.return_value.create.call_count == 2

    @pytest.mark.asyncio
    async def test_enviar_con_aprobacion_crea_pendiente_aprobacion(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        materia_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.AuditLogService") as MockAudit,
            patch("app.services.comunicacion_service.encrypt") as mock_encrypt,
        ):
            mock_encrypt.side_effect = lambda e: f"[cifrado]{e}"
            MockCR.return_value.create = AsyncMock()
            mock_tenant = Mock()
            mock_tenant.requiere_aprobacion_comunicaciones = True

            svc = ComunicacionService(tenant_id)
            svc._get_tenant = AsyncMock(return_value=mock_tenant)
            MockAudit.return_value.log = AsyncMock()

            result = await svc.enviar(
                materia_id,
                ["a@test.com"],
                "Asunto",
                "Cuerpo",
                usuario_id,
                AsyncMock(),
            )

            assert result["estado"] == "PendienteAprobacion"
            assert result["cantidad"] == 1


class TestComunicacionServiceAprobacion:
    @pytest.mark.asyncio
    async def test_aprobar_lote(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        lote_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.AuditLogService") as MockAudit,
        ):
            MockCR.return_value.batch_update_estado = AsyncMock(return_value=5)
            MockAudit.return_value.log = AsyncMock()

            svc = ComunicacionService(tenant_id)
            result = await svc.aprobar_lote(lote_id, usuario_id, AsyncMock())

            assert result["aprobadas"] == 5
            args, _ = MockCR.return_value.batch_update_estado.call_args
            assert args[1] == lote_id
            assert args[2] == "PendienteAprobacion"
            assert args[3] == "Pendiente"

    @pytest.mark.asyncio
    async def test_rechazar_lote(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        lote_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.AuditLogService") as MockAudit,
        ):
            MockCR.return_value.batch_update_estado = AsyncMock(return_value=3)
            MockAudit.return_value.log = AsyncMock()

            svc = ComunicacionService(tenant_id)
            result = await svc.rechazar_lote(lote_id, usuario_id, AsyncMock())

            assert result["rechazadas"] == 3
            args, _ = MockCR.return_value.batch_update_estado.call_args
            assert args[1] == lote_id
            assert args[2] == "PendienteAprobacion"
            assert args[3] == "Cancelado"

    @pytest.mark.asyncio
    async def test_aprobar_comunicacion_individual(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        com_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.AuditLogService") as MockAudit,
        ):
            mock_com = Mock()
            mock_com.estado = "PendienteAprobacion"
            mock_com.id = com_id
            MockCR.return_value.get = AsyncMock(return_value=mock_com)
            MockAudit.return_value.log = AsyncMock()

            svc = ComunicacionService(tenant_id)
            result = await svc.aprobar_comunicacion(com_id, usuario_id, AsyncMock())

            assert result["estado"] == "Pendiente"
            assert mock_com.estado == "Pendiente"

    @pytest.mark.asyncio
    async def test_aprobar_comunicacion_ya_enviada_raises(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        com_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        with patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR:
            mock_com = Mock()
            mock_com.estado = "Enviado"
            MockCR.return_value.get = AsyncMock(return_value=mock_com)

            svc = ComunicacionService(tenant_id)
            with pytest.raises(DomainError, match="Transición inválida"):
                await svc.aprobar_comunicacion(com_id, usuario_id, AsyncMock())


class TestComunicacionServiceCancelar:
    @pytest.mark.asyncio
    async def test_cancelar_pendiente_ok(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        com_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        with patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR:
            mock_com = Mock()
            mock_com.estado = "Pendiente"
            mock_com.id = com_id
            MockCR.return_value.get = AsyncMock(return_value=mock_com)

            svc = ComunicacionService(tenant_id)
            result = await svc.cancelar(com_id, usuario_id, AsyncMock())

            assert result["estado"] == "Cancelado"
            assert mock_com.estado == "Cancelado"

    @pytest.mark.asyncio
    async def test_cancelar_enviado_raises(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        com_id = uuid.uuid4()
        usuario_id = uuid.uuid4()

        with patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR:
            mock_com = Mock()
            mock_com.estado = "Enviado"
            MockCR.return_value.get = AsyncMock(return_value=mock_com)

            svc = ComunicacionService(tenant_id)
            with pytest.raises(DomainError, match="Transición inválida"):
                await svc.cancelar(com_id, usuario_id, AsyncMock())


class TestComunicacionServiceProcesarCola:
    @pytest.mark.asyncio
    async def test_procesa_pendiente_a_enviado(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.AuditLogService") as MockAudit,
            patch("app.services.comunicacion_service.decrypt") as mock_decrypt,
        ):
            mock_decrypt.return_value = "dest@test.com"
            mock_com = Mock()
            mock_com.estado = "Pendiente"
            mock_com.id = uuid.uuid4()
            mock_com.lote_id = uuid.uuid4()
            mock_com.materia_id = uuid.uuid4()
            mock_com.enviado_por = uuid.uuid4()
            mock_com.destinatario = "[cifrado]xxx"
            mock_com.asunto = "Asunto"
            mock_com.cuerpo = "Cuerpo"
            mock_com.intentos = 0
            MockCR.get_all_pendientes_cross_tenant = AsyncMock(return_value=[mock_com])
            MockCR.return_value.get_pendientes = AsyncMock()

            mock_audit = MockAudit.return_value
            mock_audit.log = AsyncMock()

            proveedor = _MockProveedor(debe_fallar=False)

            svc = ComunicacionService(tenant_id)
            result = await svc.procesar_cola(AsyncMock(), proveedor)

            assert result["procesadas"] == 1
            assert result["exitos"] == 1
            assert mock_com.estado == "Enviado"
            assert mock_com.intentos == 1

    @pytest.mark.asyncio
    async def test_reintenta_menos_de_3(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.AuditLogService") as MockAudit,
            patch("app.services.comunicacion_service.decrypt") as mock_decrypt,
        ):
            mock_decrypt.return_value = "dest@test.com"
            mock_com = Mock()
            mock_com.estado = "Pendiente"
            mock_com.intentos = 1
            mock_com.id = uuid.uuid4()
            mock_com.lote_id = uuid.uuid4()
            mock_com.materia_id = uuid.uuid4()
            mock_com.enviado_por = uuid.uuid4()
            mock_com.destinatario = "[cifrado]xxx"
            mock_com.asunto = "A"
            mock_com.cuerpo = "C"
            MockCR.get_all_pendientes_cross_tenant = AsyncMock(return_value=[mock_com])
            MockCR.return_value.get_pendientes = AsyncMock()

            mock_audit = MockAudit.return_value
            mock_audit.log = AsyncMock()

            proveedor = _MockProveedor(debe_fallar=True)

            svc = ComunicacionService(tenant_id)
            result = await svc.procesar_cola(AsyncMock(), proveedor)

            assert result["procesadas"] == 1
            assert result["reintentos"] == 1
            assert result["exitos"] == 0
            assert mock_com.estado == "Pendiente"
            assert mock_com.intentos == 2

    @pytest.mark.asyncio
    async def test_error_despues_de_3_intentos(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.AuditLogService") as MockAudit,
            patch("app.services.comunicacion_service.decrypt") as mock_decrypt,
        ):
            mock_decrypt.return_value = "dest@test.com"
            mock_com = Mock()
            mock_com.estado = "Pendiente"
            mock_com.intentos = 2
            mock_com.id = uuid.uuid4()
            mock_com.lote_id = uuid.uuid4()
            mock_com.materia_id = uuid.uuid4()
            mock_com.enviado_por = uuid.uuid4()
            mock_com.destinatario = "[cifrado]xxx"
            mock_com.asunto = "A"
            mock_com.cuerpo = "C"
            MockCR.get_all_pendientes_cross_tenant = AsyncMock(return_value=[mock_com])
            MockCR.return_value.get_pendientes = AsyncMock()

            mock_audit = MockAudit.return_value
            mock_audit.log = AsyncMock()

            proveedor = _MockProveedor(debe_fallar=True)

            svc = ComunicacionService(tenant_id)
            result = await svc.procesar_cola(AsyncMock(), proveedor)

            assert result["procesadas"] == 1
            assert result["errores"] == 1
            assert result["exitos"] == 0
            assert mock_com.estado == "Error"
            assert mock_com.intentos == 3


class TestComunicacionServiceListar:
    @pytest.mark.asyncio
    async def test_listar_comunicaciones(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.decrypt") as mock_decrypt,
        ):
            mock_decrypt.return_value = "dest@test.com"
            mock_com = Mock()
            mock_com.id = uuid.uuid4()
            mock_com.tenant_id = tenant_id
            mock_com.enviado_por = uuid.uuid4()
            mock_com.materia_id = uuid.uuid4()
            mock_com.destinatario = "[cifrado]xxx"
            mock_com.asunto = "Asunto"
            mock_com.cuerpo = "Cuerpo"
            mock_com.lote_id = uuid.uuid4()
            mock_com.intentos = 0
            mock_com.error_msg = None
            mock_com.estado = "Pendiente"
            mock_com.enviado_at = None
            mock_com.enqueue_at = None
            mock_com.created_at = None
            MockCR.return_value.get_all = AsyncMock(return_value=[mock_com])

            svc = ComunicacionService(tenant_id)
            result = await svc.listar(AsyncMock(), lote_id=mock_com.lote_id)

            assert result["total"] == 1
            assert len(result["items"]) == 1
            assert result["items"][0]["destinatario"] == "dest@test.com"
            assert result["items"][0]["estado"] == "Pendiente"

    @pytest.mark.asyncio
    async def test_obtener_comunicacion(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        com_id = uuid.uuid4()

        with (
            patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR,
            patch("app.services.comunicacion_service.decrypt") as mock_decrypt,
        ):
            mock_decrypt.return_value = "dest@test.com"
            mock_com = Mock()
            mock_com.id = com_id
            mock_com.tenant_id = tenant_id
            mock_com.enviado_por = uuid.uuid4()
            mock_com.materia_id = uuid.uuid4()
            mock_com.destinatario = "[cifrado]xxx"
            mock_com.asunto = "A"
            mock_com.cuerpo = "C"
            mock_com.lote_id = uuid.uuid4()
            mock_com.intentos = 0
            mock_com.error_msg = None
            mock_com.estado = "Pendiente"
            mock_com.enviado_at = None
            mock_com.enqueue_at = None
            mock_com.created_at = None
            MockCR.return_value.get = AsyncMock(return_value=mock_com)

            svc = ComunicacionService(tenant_id)
            result = await svc.obtener(com_id, AsyncMock())

            assert result is not None
            assert result["destinatario"] == "dest@test.com"

    @pytest.mark.asyncio
    async def test_obtener_no_existe(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()

        with patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR:
            MockCR.return_value.get = AsyncMock(return_value=None)

            svc = ComunicacionService(tenant_id)
            result = await svc.obtener(uuid.uuid4(), AsyncMock())

            assert result is None

    @pytest.mark.asyncio
    async def test_listar_lotes(self):
        from app.services.comunicacion_service import ComunicacionService
        tenant_id = uuid.uuid4()
        lote_id = uuid.uuid4()

        with patch("app.services.comunicacion_service.ComunicacionRepository") as MockCR:
            mock_c1 = Mock()
            mock_c1.lote_id = lote_id
            mock_c1.estado = "Pendiente"
            mock_c1.enqueue_at = None
            mock_c2 = Mock()
            mock_c2.lote_id = lote_id
            mock_c2.estado = "Enviado"
            mock_c2.enqueue_at = None

            MockCR.return_value.get_all = AsyncMock(return_value=[mock_c1, mock_c2])

            svc = ComunicacionService(tenant_id)
            result = await svc.listar_lotes(AsyncMock())

            assert len(result) == 1
            assert result[0]["total"] == 2
            assert result[0]["conteo_por_estado"]["Pendiente"] == 1
            assert result[0]["conteo_por_estado"]["Enviado"] == 1


class TestComunicacionSchemas:
    def test_comunicacion_response_has_fields(self):
        from app.schemas.comunicacion import ComunicacionResponse
        fields = ComunicacionResponse.model_fields
        assert "id" in fields
        assert "destinatario" in fields
        assert "asunto" in fields
        assert "cuerpo" in fields
        assert "estado" in fields
        assert "lote_id" in fields

    def test_preview_request_has_fields(self):
        from app.schemas.comunicacion import PreviewRequest
        fields = PreviewRequest.model_fields
        assert "materia_id" in fields
        assert "destinatario_email" in fields
        assert "asunto_template" in fields
        assert "cuerpo_template" in fields

    def test_crear_comunicacion_request_has_fields(self):
        from app.schemas.comunicacion import CrearComunicacionRequest
        fields = CrearComunicacionRequest.model_fields
        assert "materia_id" in fields
        assert "destinatarios" in fields
        assert "asunto_template" in fields
        assert "cuerpo_template" in fields

    def test_lote_response_has_counts(self):
        from app.schemas.comunicacion import LoteResponse
        fields = LoteResponse.model_fields
        assert "lote_id" in fields
        assert "total" in fields
        assert "conteo_por_estado" in fields


class TestMockProveedorEnvio:
    @pytest.mark.asyncio
    async def test_enviar_exitoso(self):
        from app.workers.comunicacion_worker import MockProveedorEnvio
        proveedor = MockProveedorEnvio()
        await proveedor.enviar("dest@test.com", "Asunto", "Cuerpo")
        assert proveedor.enviados == 1

    @pytest.mark.asyncio
    async def test_enviar_falla_si_configured(self):
        from app.workers.comunicacion_worker import MockProveedorEnvio
        proveedor = MockProveedorEnvio(debe_fallar=True)
        with pytest.raises(RuntimeError, match="Simulated error"):
            await proveedor.enviar("dest@test.com", "A", "C")


class _MockSession:
    def __init__(self) -> None:
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        execute_result = MagicMock()
        execute_result.scalars.return_value.all.return_value = []
        self.execute = AsyncMock(return_value=execute_result)
        self.flush = AsyncMock()
        self.refresh = AsyncMock()
        self.close = AsyncMock()
        self.add = MagicMock()
        self.get = AsyncMock()


@pytest.fixture
def async_client_com():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


class TestComunicacionEndpoints:
    @pytest.fixture(autouse=True)
    def mock_deps(self):
        user_id = uuid.uuid4()
        tenant_id = uuid.uuid4()

        async def _mock_user():
            user = Mock(spec=User)
            user.id = user_id
            user.tenant_id = tenant_id
            user.is_active = True
            user.impersonator_id = None
            return user

        async def _mock_db():
            return _MockSession()

        app.dependency_overrides[get_current_user] = _mock_user
        app.dependency_overrides[get_db] = _mock_db
        yield
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_preview_returns_200(self, async_client_com):
        materia_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.preview = AsyncMock(return_value={"asunto": "Hola Juan", "cuerpo": "Test"})

            response = await async_client_com.post(
                "/api/comunicaciones/preview",
                json={
                    "materia_id": materia_id,
                    "destinatario_email": "juan@test.com",
                    "asunto_template": "Hola $nombre",
                    "cuerpo_template": "Test $nombre",
                },
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["asunto"] == "Hola Juan"

    @pytest.mark.asyncio
    async def test_enviar_returns_201(self, async_client_com):
        materia_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.enviar = AsyncMock(return_value={"lote_id": str(uuid.uuid4()), "cantidad": 2, "estado": "Pendiente"})

            response = await async_client_com.post(
                "/api/comunicaciones/enviar",
                json={
                    "materia_id": materia_id,
                    "destinatarios": ["a@test.com", "b@test.com"],
                    "asunto_template": "Asunto",
                    "cuerpo_template": "Cuerpo",
                },
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_listar_comunicaciones_returns_200(self, async_client_com):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar = AsyncMock(return_value={"items": [], "total": 0, "pagina": 1, "por_pagina": 50})

            response = await async_client_com.get(
                "/api/comunicaciones",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_obtener_comunicacion_returns_200(self, async_client_com):
        com_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener = AsyncMock(return_value={
                "id": com_id, "tenant_id": str(uuid.uuid4()), "enviado_por": str(uuid.uuid4()),
                "materia_id": str(uuid.uuid4()), "destinatario": "a@test.com",
                "asunto": "A", "cuerpo": "C", "estado": "Pendiente",
            })

            response = await async_client_com.get(
                f"/api/comunicaciones/{com_id}",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_obtener_comunicacion_404(self, async_client_com):
        com_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener = AsyncMock(return_value=None)

            response = await async_client_com.get(
                f"/api/comunicaciones/{com_id}",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_cancelar_returns_200(self, async_client_com):
        com_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.cancelar = AsyncMock(return_value={"estado": "Cancelado"})

            response = await async_client_com.post(
                f"/api/comunicaciones/{com_id}/cancelar",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_listar_lotes_returns_200(self, async_client_com):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_lotes = AsyncMock(return_value=[{"lote_id": str(uuid.uuid4()), "total": 5, "conteo_por_estado": {"Pendiente": 5}}])

            response = await async_client_com.get(
                "/api/comunicaciones/lotes",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_aprobar_lote_returns_200(self, async_client_com):
        lote_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.aprobar_lote = AsyncMock(return_value={"lote_id": lote_id, "aprobadas": 5})

            response = await async_client_com.post(
                f"/api/comunicaciones/lotes/{lote_id}/aprobar",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rechazar_lote_returns_200(self, async_client_com):
        lote_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.rechazar_lote = AsyncMock(return_value={"lote_id": lote_id, "rechazadas": 3})

            response = await async_client_com.post(
                f"/api/comunicaciones/lotes/{lote_id}/rechazar",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_aprobar_comunicacion_individual_returns_200(self, async_client_com):
        com_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.comunicaciones.ComunicacionService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.aprobar_comunicacion = AsyncMock(return_value={"comunicacion_id": com_id, "estado": "Pendiente"})

            response = await async_client_com.post(
                f"/api/comunicaciones/{com_id}/aprobar",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sin_permiso_returns_403(self, async_client_com):
        with patch("app.core.permissions.decode_access_token", return_value={"rols": []}):
            response = await async_client_com.get(
                "/api/comunicaciones",
                headers={"Authorization": "Bearer no-perms"},
            )
            assert response.status_code == 403


class TestComunicacionWorker:
    @pytest.mark.asyncio
    async def test_iteracion_usa_session_factory(self):
        from app.workers.comunicacion_worker import ComunicacionWorker
        mock_service = AsyncMock()
        mock_service.procesar_cola = AsyncMock(return_value={"procesadas": 2, "exitos": 2, "reintentos": 0, "errores": 0})

        mock_session = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_factory = Mock(return_value=mock_cm)

        worker = ComunicacionWorker(session_factory=mock_factory, poll_interval=0.01)
        worker._service = mock_service

        await worker._iteracion()

        mock_service.procesar_cola.assert_called_once()

    @pytest.mark.asyncio
    async def test_worker_graceful_shutdown_on_cancelled(self):
        from app.workers.comunicacion_worker import ComunicacionWorker
        worker = ComunicacionWorker(session_factory=Mock(), poll_interval=0.01)
        worker._service = AsyncMock()

        async def raise_cancelled():
            raise asyncio.CancelledError

        worker._iteracion = raise_cancelled

        await worker.run()
        assert worker._running is False

    @pytest.mark.asyncio
    async def test_worker_loop_calls_iteracion_repeatedly(self):
        from app.workers.comunicacion_worker import ComunicacionWorker
        calls = []

        async def tracking_iteracion():
            calls.append(1)
            if len(calls) >= 3:
                raise asyncio.CancelledError

        worker = ComunicacionWorker(session_factory=Mock(), poll_interval=0.01)
        worker._service = AsyncMock()
        worker._iteracion = tracking_iteracion

        await worker.run()

        assert len(calls) == 3
        assert worker._running is False
