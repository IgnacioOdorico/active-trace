import uuid
from datetime import date, time

import pytest

from app.core.exceptions import DomainError


class TestDiaSemana:
    def test_enum_values(self):
        from app.models.slot_encuentro import DiaSemana
        assert DiaSemana.LUNES.value == "Lunes"
        assert DiaSemana.MARTES.value == "Martes"
        assert DiaSemana.MIERCOLES.value == "Miércoles"
        assert DiaSemana.JUEVES.value == "Jueves"
        assert DiaSemana.VIERNES.value == "Viernes"
        assert DiaSemana.SABADO.value == "Sábado"
        assert DiaSemana.DOMINGO.value == "Domingo"

    def test_enum_all_members_present(self):
        from app.models.slot_encuentro import DiaSemana
        expected = {"Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"}
        actual = {m.value for m in DiaSemana}
        assert actual == expected


class TestEstadoEncuentro:
    def test_enum_values(self):
        from app.models.instancia_encuentro import EstadoEncuentro
        assert EstadoEncuentro.PROGRAMADO.value == "Programado"
        assert EstadoEncuentro.REALIZADO.value == "Realizado"
        assert EstadoEncuentro.CANCELADO.value == "Cancelado"

    def test_enum_all_members_present(self):
        from app.models.instancia_encuentro import EstadoEncuentro
        expected = {"Programado", "Realizado", "Cancelado"}
        actual = {m.value for m in EstadoEncuentro}
        assert actual == expected


class TestEstadoGuardia:
    def test_enum_values(self):
        from app.models.guardia import EstadoGuardia
        assert EstadoGuardia.PENDIENTE.value == "Pendiente"
        assert EstadoGuardia.REALIZADA.value == "Realizada"
        assert EstadoGuardia.CANCELADA.value == "Cancelada"

    def test_enum_all_members_present(self):
        from app.models.guardia import EstadoGuardia
        expected = {"Pendiente", "Realizada", "Cancelada"}
        actual = {m.value for m in EstadoGuardia}
        assert actual == expected


class TestSlotEncuentroModel:
    def test_tablename(self):
        from app.models.slot_encuentro import SlotEncuentro
        assert SlotEncuentro.__tablename__ == "slot_encuentro"

    def test_has_entity_meta_fields(self):
        from app.models.slot_encuentro import SlotEncuentro
        assert hasattr(SlotEncuentro, "id")
        assert hasattr(SlotEncuentro, "tenant_id")
        assert hasattr(SlotEncuentro, "created_at")
        assert hasattr(SlotEncuentro, "updated_at")
        assert hasattr(SlotEncuentro, "deleted_at")

    def test_has_slot_fields(self):
        from app.models.slot_encuentro import SlotEncuentro
        assert hasattr(SlotEncuentro, "asignacion_id")
        assert hasattr(SlotEncuentro, "materia_id")
        assert hasattr(SlotEncuentro, "titulo")
        assert hasattr(SlotEncuentro, "hora")
        assert hasattr(SlotEncuentro, "dia_semana")
        assert hasattr(SlotEncuentro, "fecha_inicio")
        assert hasattr(SlotEncuentro, "cant_semanas")
        assert hasattr(SlotEncuentro, "fecha_unica")
        assert hasattr(SlotEncuentro, "meet_url")
        assert hasattr(SlotEncuentro, "vig_desde")
        assert hasattr(SlotEncuentro, "vig_hasta")

    def test_titulo_string_200(self):
        from app.models.slot_encuentro import SlotEncuentro
        col = SlotEncuentro.__mapper__.columns["titulo"]
        assert col.type.length == 200
        assert col.nullable is False

    def test_fecha_unica_nullable(self):
        from app.models.slot_encuentro import SlotEncuentro
        col = SlotEncuentro.__mapper__.columns["fecha_unica"]
        assert col.nullable is True

    def test_cant_semanas_default_0(self):
        from app.models.slot_encuentro import SlotEncuentro
        col = SlotEncuentro.__mapper__.columns["cant_semanas"]
        assert col.default is not None
        assert col.nullable is False

    def test_vig_hasta_nullable(self):
        from app.models.slot_encuentro import SlotEncuentro
        col = SlotEncuentro.__mapper__.columns["vig_hasta"]
        assert col.nullable is True

    def test_asignacion_id_fk(self):
        from app.models.slot_encuentro import SlotEncuentro
        col = SlotEncuentro.__mapper__.columns["asignacion_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "asignaciones"

    def test_materia_id_fk(self):
        from app.models.slot_encuentro import SlotEncuentro
        col = SlotEncuentro.__mapper__.columns["materia_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "materias"


class TestInstanciaEncuentroModel:
    def test_tablename(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        assert InstanciaEncuentro.__tablename__ == "instancia_encuentro"

    def test_has_entity_meta_fields(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        assert hasattr(InstanciaEncuentro, "id")
        assert hasattr(InstanciaEncuentro, "tenant_id")
        assert hasattr(InstanciaEncuentro, "created_at")
        assert hasattr(InstanciaEncuentro, "updated_at")
        assert hasattr(InstanciaEncuentro, "deleted_at")

    def test_has_instance_fields(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        assert hasattr(InstanciaEncuentro, "slot_id")
        assert hasattr(InstanciaEncuentro, "materia_id")
        assert hasattr(InstanciaEncuentro, "fecha")
        assert hasattr(InstanciaEncuentro, "hora")
        assert hasattr(InstanciaEncuentro, "titulo")
        assert hasattr(InstanciaEncuentro, "estado")
        assert hasattr(InstanciaEncuentro, "meet_url")
        assert hasattr(InstanciaEncuentro, "video_url")
        assert hasattr(InstanciaEncuentro, "comentario")

    def test_slot_id_nullable(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        col = InstanciaEncuentro.__mapper__.columns["slot_id"]
        assert col.nullable is True

    def test_video_url_nullable(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        col = InstanciaEncuentro.__mapper__.columns["video_url"]
        assert col.nullable is True

    def test_comentario_nullable(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        col = InstanciaEncuentro.__mapper__.columns["comentario"]
        assert col.nullable is True

    def test_estado_default(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        col = InstanciaEncuentro.__mapper__.columns["estado"]
        assert col.default is not None

    def test_estado_string_20(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        col = InstanciaEncuentro.__mapper__.columns["estado"]
        assert col.type.length == 20

    def test_materia_id_fk(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        col = InstanciaEncuentro.__mapper__.columns["materia_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "materias"

    def test_slot_id_fk(self):
        from app.models.instancia_encuentro import InstanciaEncuentro
        col = InstanciaEncuentro.__mapper__.columns["slot_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "slot_encuentro"


class TestGuardiaModel:
    def test_tablename(self):
        from app.models.guardia import Guardia
        assert Guardia.__tablename__ == "guardia"

    def test_has_entity_meta_fields(self):
        from app.models.guardia import Guardia
        assert hasattr(Guardia, "id")
        assert hasattr(Guardia, "tenant_id")
        assert hasattr(Guardia, "created_at")
        assert hasattr(Guardia, "updated_at")
        assert hasattr(Guardia, "deleted_at")

    def test_has_guardia_fields(self):
        from app.models.guardia import Guardia
        assert hasattr(Guardia, "asignacion_id")
        assert hasattr(Guardia, "materia_id")
        assert hasattr(Guardia, "carrera_id")
        assert hasattr(Guardia, "cohorte_id")
        assert hasattr(Guardia, "dia")
        assert hasattr(Guardia, "horario")
        assert hasattr(Guardia, "estado")
        assert hasattr(Guardia, "comentarios")

    def test_cohorte_id_nullable(self):
        from app.models.guardia import Guardia
        col = Guardia.__mapper__.columns["cohorte_id"]
        assert col.nullable is True

    def test_comentarios_nullable(self):
        from app.models.guardia import Guardia
        col = Guardia.__mapper__.columns["comentarios"]
        assert col.nullable is True

    def test_estado_default(self):
        from app.models.guardia import Guardia
        col = Guardia.__mapper__.columns["estado"]
        assert col.default is not None

    def test_estado_string_20(self):
        from app.models.guardia import Guardia
        col = Guardia.__mapper__.columns["estado"]
        assert col.type.length == 20

    def test_asignacion_id_fk(self):
        from app.models.guardia import Guardia
        col = Guardia.__mapper__.columns["asignacion_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "asignaciones"

    def test_materia_id_fk(self):
        from app.models.guardia import Guardia
        col = Guardia.__mapper__.columns["materia_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "materias"

    def test_carrera_id_fk(self):
        from app.models.guardia import Guardia
        col = Guardia.__mapper__.columns["carrera_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "carreras"
