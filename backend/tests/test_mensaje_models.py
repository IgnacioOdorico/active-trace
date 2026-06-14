import uuid

import pytest

from app.models.mensaje import Mensaje
from app.models.user import User


class TestMensajeModel:
    def test_mensaje_tablename(self):
        assert Mensaje.__tablename__ == "mensajes"

    def test_mensaje_inherits_entity_meta(self):
        assert hasattr(Mensaje, "id")
        assert hasattr(Mensaje, "tenant_id")
        assert hasattr(Mensaje, "deleted_at")

    def test_mensaje_has_required_fields(self):
        assert hasattr(Mensaje, "remitente_id")
        assert hasattr(Mensaje, "destinatario_id")
        assert hasattr(Mensaje, "asunto")
        assert hasattr(Mensaje, "cuerpo")
        assert hasattr(Mensaje, "leido")
        assert hasattr(Mensaje, "thread_id")

    def test_mensaje_thread_id_nullable(self):
        col = Mensaje.__mapper__.columns["thread_id"]
        assert col.nullable

    def test_mensaje_leido_default_false(self):
        col = Mensaje.__mapper__.columns["leido"]
        assert col.default is not None and col.default.arg is False

    def test_mensaje_asunto_length_200(self):
        col = Mensaje.__mapper__.columns["asunto"]
        assert col.type.length == 200

    def test_mensaje_cuerpo_is_text(self):
        col = Mensaje.__mapper__.columns["cuerpo"]
        assert str(col.type) == "TEXT"

    def test_mensaje_remitente_not_nullable(self):
        col = Mensaje.__mapper__.columns["remitente_id"]
        assert not col.nullable

    def test_mensaje_destinatario_not_nullable(self):
        col = Mensaje.__mapper__.columns["destinatario_id"]
        assert not col.nullable

    def test_mensaje_has_relations(self):
        assert hasattr(Mensaje, "remitente")
        assert hasattr(Mensaje, "destinatario")

    def test_mensaje_thread_self_referential(self):
        col = Mensaje.__mapper__.columns["thread_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        fk = fks[0]
        assert fk.column.table.name == "mensajes"
        assert fk.column.name == "id"

    def test_mensaje_thread_id_indexed(self):
        col = Mensaje.__mapper__.columns["thread_id"]
        assert col.index is True
