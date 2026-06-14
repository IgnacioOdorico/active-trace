import uuid
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest

from app.models.mensaje import Mensaje


class TestMensajeRepository:
    _tenant_id = uuid.uuid4()
    _user_id = uuid.uuid4()
    _other_user_id = uuid.uuid4()
    _root_id = uuid.uuid4()

    def _make_mock_mensaje(
        self,
        id: uuid.UUID,
        remitente_id: uuid.UUID,
        destinatario_id: uuid.UUID,
        thread_id: uuid.UUID | None = None,
        asunto: str = "Test",
        cuerpo: str = "Body",
    ) -> Mock:
        msg = Mock(spec=Mensaje)
        msg.id = id
        msg.tenant_id = self._tenant_id
        msg.remitente_id = remitente_id
        msg.destinatario_id = destinatario_id
        msg.thread_id = thread_id
        msg.asunto = asunto
        msg.cuerpo = cuerpo
        msg.leido = False
        type(msg).remitente = PropertyMock(return_value=None)
        type(msg).destinatario = PropertyMock(return_value=None)
        return msg

    # --- 3.1 (RED): listar_hilos ---

    def test_repository_inherits_base(self):
        from app.repositories.base import BaseRepository
        from app.repositories.mensaje_repository import MensajeRepository

        assert issubclass(MensajeRepository, BaseRepository)

    def test_repository_init_with_mensaje_model(self):
        from app.repositories.mensaje_repository import MensajeRepository

        repo = MensajeRepository(self._tenant_id)
        assert repo._model == Mensaje
        assert repo._tenant_id == self._tenant_id

    @pytest.mark.asyncio
    async def test_listar_hilos_has_method(self):
        from app.repositories.mensaje_repository import MensajeRepository

        repo = MensajeRepository(self._tenant_id)
        assert hasattr(repo, "listar_hilos")

    @pytest.mark.asyncio
    async def test_obtener_hilo_has_method(self):
        from app.repositories.mensaje_repository import MensajeRepository

        repo = MensajeRepository(self._tenant_id)
        assert hasattr(repo, "obtener_hilo")

    @pytest.mark.asyncio
    async def test_responder_has_method(self):
        from app.repositories.mensaje_repository import MensajeRepository

        repo = MensajeRepository(self._tenant_id)
        assert hasattr(repo, "responder")

    @pytest.mark.asyncio
    async def test_listar_hilos_returns_paginated_results(self):
        from app.repositories.mensaje_repository import MensajeRepository

        mock_session = AsyncMock()
        mr = Mock()
        mr.scalar_one.return_value = 1
        mr.scalars.return_value.all.return_value = [
            self._make_mock_mensaje(
                self._root_id, self._other_user_id, self._user_id
            )
        ]
        mr.unique.return_value = mr
        mock_session.execute = AsyncMock(return_value=mr)

        repo = MensajeRepository(self._tenant_id)
        items, total = await repo.listar_hilos(
            mock_session, self._user_id, pagina=1, page_size=20
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].id == self._root_id

    # --- 3.3 (RED): obtener_hilo ---

    @pytest.mark.asyncio
    async def test_obtener_hilo_returns_root_with_responses(self):
        from app.repositories.mensaje_repository import MensajeRepository

        mock_root = self._make_mock_mensaje(
            self._root_id, self._other_user_id, self._user_id
        )
        mock_reply = self._make_mock_mensaje(
            uuid.uuid4(), self._user_id, self._other_user_id,
            thread_id=self._root_id,
        )

        mock_session = AsyncMock()
        mr = Mock()
        mr.scalars.return_value.all.return_value = [mock_root, mock_reply]
        mr.unique.return_value = mr
        mock_session.execute = AsyncMock(return_value=mr)

        repo = MensajeRepository(self._tenant_id)
        result = await repo.obtener_hilo(mock_session, self._root_id)

        assert result is not None
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_obtener_hilo_empty_returns_empty_list(self):
        from app.repositories.mensaje_repository import MensajeRepository

        mock_session = AsyncMock()
        mr = Mock()
        mr.scalars.return_value.all.return_value = []
        mr.unique.return_value = mr
        mock_session.execute = AsyncMock(return_value=mr)

        repo = MensajeRepository(self._tenant_id)
        result = await repo.obtener_hilo(mock_session, uuid.uuid4())

        assert result == []

    # --- 3.5 (TRIANGULATE): responder creates msg with correct thread_id ---

    @pytest.mark.asyncio
    async def test_responder_creates_message(self):
        from unittest.mock import patch

        from app.repositories.mensaje_repository import MensajeRepository

        mock_session = AsyncMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch.object(MensajeRepository, "create") as mock_create:
            expected = self._make_mock_mensaje(
                uuid.uuid4(), self._user_id, self._other_user_id,
                thread_id=self._root_id, asunto="Re: Test", cuerpo="Response body",
            )
            expected.leido = False
            mock_create.return_value = expected

            repo = MensajeRepository(self._tenant_id)
            result = await repo.responder(
                mock_session,
                remitente_id=self._user_id,
                destinatario_id=self._other_user_id,
                thread_id=self._root_id,
                asunto="Re: Test",
                cuerpo="Response body",
            )

            assert result.thread_id == self._root_id
            assert result.remitente_id == self._user_id
            assert result.destinatario_id == self._other_user_id
            assert result.asunto == "Re: Test"
            assert result.cuerpo == "Response body"
            assert result.leido is False
