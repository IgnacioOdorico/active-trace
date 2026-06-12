import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.models.mensaje import Mensaje


class TestInboxService:
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
        return msg

    # --- 5.1 (RED): InboxService.listar_hilos ---

    @pytest.mark.asyncio
    async def test_listar_hilos_returns_paginated_threads(self):
        from app.services.inbox_service import InboxService

        mock_db = AsyncMock()
        mock_root = self._make_mock_mensaje(
            self._root_id, self._other_user_id, self._user_id,
            asunto="Hola", cuerpo="Mensaje de prueba",
        )

        with patch("app.services.inbox_service.MensajeRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.listar_hilos = AsyncMock(
                return_value=([mock_root], 1)
            )

            svc = InboxService(self._tenant_id)
            items, total = await svc.listar_hilos(
                mock_db, self._user_id, pagina=1, page_size=20
            )

            assert total == 1
            assert len(items) == 1
            assert items[0]["id"] == str(self._root_id)
            assert items[0]["asunto"] == "Hola"
            assert items[0]["ultimo_mensaje"] == "Mensaje de prueba"

    @pytest.mark.asyncio
    async def test_listar_hilos_empty_returns_empty(self):
        from app.services.inbox_service import InboxService

        mock_db = AsyncMock()

        with patch("app.services.inbox_service.MensajeRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.listar_hilos = AsyncMock(return_value=([], 0))

            svc = InboxService(self._tenant_id)
            items, total = await svc.listar_hilos(
                mock_db, self._user_id, pagina=1, page_size=20
            )

            assert total == 0
            assert items == []

    # --- 5.3 (RED): InboxService.obtener_hilo ---

    @pytest.mark.asyncio
    async def test_obtener_hilo_returns_full_thread(self):
        from app.services.inbox_service import InboxService

        mock_db = AsyncMock()
        mock_root = self._make_mock_mensaje(
            self._root_id, self._other_user_id, self._user_id,
            asunto="Hola", cuerpo="Mensaje raíz",
        )
        mock_reply = self._make_mock_mensaje(
            uuid.uuid4(), self._user_id, self._other_user_id,
            thread_id=self._root_id, asunto="Re: Hola", cuerpo="Respuesta",
        )

        with patch("app.services.inbox_service.MensajeRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.obtener_hilo = AsyncMock(return_value=[mock_root, mock_reply])

            svc = InboxService(self._tenant_id)
            result = await svc.obtener_hilo(mock_db, self._user_id, self._root_id)

            assert result is not None
            assert result["id"] == str(self._root_id)
            assert len(result["respuestas"]) == 1
            assert result["respuestas"][0]["cuerpo"] == "Respuesta"

    @pytest.mark.asyncio
    async def test_obtener_hilo_raises_not_found_for_empty(self):
        from app.core.exceptions import EntityNotFoundError
        from app.services.inbox_service import InboxService

        mock_db = AsyncMock()

        with patch("app.services.inbox_service.MensajeRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.obtener_hilo = AsyncMock(return_value=[])

            svc = InboxService(self._tenant_id)
            with pytest.raises(EntityNotFoundError):
                await svc.obtener_hilo(mock_db, self._user_id, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_obtener_hilo_raises_not_found_for_not_participant(self):
        from app.core.exceptions import EntityNotFoundError
        from app.services.inbox_service import InboxService

        mock_db = AsyncMock()
        stranger_id = uuid.uuid4()
        mock_root = self._make_mock_mensaje(
            self._root_id, self._other_user_id, self._user_id,
        )

        with patch("app.services.inbox_service.MensajeRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.obtener_hilo = AsyncMock(return_value=[mock_root])

            svc = InboxService(self._tenant_id)
            with pytest.raises(EntityNotFoundError):
                await svc.obtener_hilo(mock_db, stranger_id, self._root_id)

    # --- 5.5 (RED): InboxService.responder ---

    @pytest.mark.asyncio
    async def test_responder_creates_reply_in_thread(self):
        from app.services.inbox_service import InboxService

        mock_db = AsyncMock()
        mock_root = self._make_mock_mensaje(
            self._root_id, self._other_user_id, self._user_id,
            asunto="Hola", cuerpo="Mensaje raíz",
        )
        mock_reply = self._make_mock_mensaje(
            uuid.uuid4(), self._user_id, self._other_user_id,
            thread_id=self._root_id, asunto="Re: Hola", cuerpo="Mi respuesta",
        )

        with patch("app.services.inbox_service.MensajeRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.obtener_hilo = AsyncMock(return_value=[mock_root])
            mock_repo.responder = AsyncMock(return_value=mock_reply)

            svc = InboxService(self._tenant_id)
            result = await svc.responder(
                mock_db, self._user_id, self._root_id, "Mi respuesta"
            )

            assert result["thread_id"] == str(self._root_id)
            assert result["cuerpo"] == "Mi respuesta"
            assert result["remitente_id"] == str(self._user_id)

    @pytest.mark.asyncio
    async def test_responder_raises_not_found_for_non_participant(self):
        from app.core.exceptions import EntityNotFoundError
        from app.services.inbox_service import InboxService

        mock_db = AsyncMock()
        stranger_id = uuid.uuid4()
        mock_root = self._make_mock_mensaje(
            self._root_id, self._other_user_id, self._user_id,
        )

        with patch("app.services.inbox_service.MensajeRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.obtener_hilo = AsyncMock(return_value=[mock_root])

            svc = InboxService(self._tenant_id)
            with pytest.raises(EntityNotFoundError):
                await svc.responder(mock_db, stranger_id, self._root_id, "Nope")
