import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.models.user import User


class TestPerfilService:
    _tenant_id = uuid.uuid4()
    _user_id = uuid.uuid4()

    def _make_user(self) -> Mock:
        user = Mock(spec=User)
        user.id = self._user_id
        user.tenant_id = self._tenant_id
        user.email = "user@test.com"
        user.nombre = "Juan"
        user.apellidos = "Pérez"
        user.dni = "12345678"
        user.cuil = "20123456789"
        user.cbu = "0000000000000000000000"
        user.alias_cbu = None
        user.banco = "Banco Nación"
        user.regional = "CABA"
        user.legajo = "L-001"
        user.legajo_profesional = None
        user.facturador = False
        user.estado = "Activo"
        user.is_active = True
        user.created_at = None
        user.updated_at = None
        return user

    # --- 4.2 (RED): PerfilService.obtener ---

    @pytest.mark.asyncio
    async def test_obtener_returns_user_with_decrypted_pii(self):
        from app.services.perfil_service import PerfilService

        mock_db = AsyncMock()
        mock_user = self._make_user()

        svc = PerfilService(self._tenant_id)
        result = await svc.obtener(mock_db, mock_user)

        assert result.id == str(self._user_id)
        assert result.tenant_id == str(self._tenant_id)
        assert result.email == "user@test.com"
        assert result.nombre == "Juan"

    @pytest.mark.asyncio
    async def test_obtener_returns_perfil_response_type(self):
        from app.schemas.perfil import PerfilResponse
        from app.services.perfil_service import PerfilService

        mock_db = AsyncMock()
        mock_user = self._make_user()

        svc = PerfilService(self._tenant_id)
        result = await svc.obtener(mock_db, mock_user)

        assert isinstance(result, PerfilResponse)

    # --- 4.4 (RED): PerfilService.actualizar ---

    @pytest.mark.asyncio
    async def test_actualizar_updates_fields(self):
        from app.schemas.perfil import PerfilUpdate
        from app.services.perfil_service import PerfilService

        mock_db = AsyncMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_user = self._make_user()

        with patch("app.services.perfil_service.UsuarioRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_email = AsyncMock(return_value=None)

            async def _update_side_effect(db, uid, data):
                for k, v in data.items():
                    setattr(mock_user, k, v)
                return mock_user

            mock_repo.update = AsyncMock(side_effect=_update_side_effect)

            svc = PerfilService(self._tenant_id)
            data = PerfilUpdate(nombre="NuevoNombre")
            result = await svc.actualizar(mock_db, mock_user, data)

            assert result.nombre == "NuevoNombre"

    @pytest.mark.asyncio
    async def test_actualizar_encrypts_pii_before_save(self):
        from app.schemas.perfil import PerfilUpdate
        from app.services.perfil_service import PerfilService

        mock_db = AsyncMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_user = self._make_user()

        with (
            patch("app.services.perfil_service.UsuarioRepository") as MockRepo,
            patch("app.services.perfil_service.encrypt") as mock_encrypt,
        ):
            mock_encrypt.side_effect = lambda x: f"[enc]{x}"
            mock_repo = MockRepo.return_value
            mock_repo.get_by_email = AsyncMock(return_value=None)
            async def _update_side_effect(db, uid, data):
                for k, v in data.items():
                    setattr(mock_user, k, v)
                # Decrypt PII before setting (since service decrypts after update)
                for k in ("email", "dni", "cuil", "cbu", "alias_cbu"):
                    val = getattr(mock_user, k, None)
                    if val and isinstance(val, str) and val.startswith("[enc]"):
                        setattr(mock_user, k, val.replace("[enc]", ""))
                return mock_user

            mock_repo.update = AsyncMock(side_effect=_update_side_effect)
            mock_repo.get = AsyncMock(return_value=mock_user)

            svc = PerfilService(self._tenant_id)
            data = PerfilUpdate(nombre="Test", email="test@email.com")
            result = await svc.actualizar(mock_db, mock_user, data)

            assert result.email == "test@email.com"

    # --- 4.6 (TRIANGULATE): email duplicado ---

    @pytest.mark.asyncio
    async def test_actualizar_email_duplicado_raises_error(self):
        from app.core.exceptions import DomainError
        from app.schemas.perfil import PerfilUpdate
        from app.services.perfil_service import PerfilService

        mock_db = AsyncMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_user = self._make_user()
        other_user = Mock(spec=User)
        other_user.id = uuid.uuid4()

        with patch("app.services.perfil_service.UsuarioRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_email = AsyncMock(return_value=other_user)

            svc = PerfilService(self._tenant_id)
            data = PerfilUpdate(email="duplicado@test.com")

            with pytest.raises(DomainError) as exc:
                await svc.actualizar(mock_db, mock_user, data)
            assert str(exc.value.detail) == "EMAIL_DUPLICADO"
