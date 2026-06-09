from datetime import datetime, timedelta, timezone

from app.models.asignacion import Asignacion


class TestAsignacionModel:
    def test_asignacion_tablename(self):
        assert Asignacion.__tablename__ == "asignaciones"

    def test_asignacion_has_usuario_id(self):
        assert hasattr(Asignacion, "usuario_id")

    def test_asignacion_has_rol(self):
        assert hasattr(Asignacion, "rol")

    def test_asignacion_has_materia_id(self):
        assert hasattr(Asignacion, "materia_id")

    def test_asignacion_has_carrera_id(self):
        assert hasattr(Asignacion, "carrera_id")

    def test_asignacion_has_cohorte_id(self):
        assert hasattr(Asignacion, "cohorte_id")

    def test_asignacion_has_comisiones(self):
        assert hasattr(Asignacion, "comisiones")

    def test_asignacion_has_responsable_id(self):
        assert hasattr(Asignacion, "responsable_id")

    def test_asignacion_has_desde(self):
        assert hasattr(Asignacion, "desde")

    def test_asignacion_has_hasta(self):
        assert hasattr(Asignacion, "hasta")

    def test_asignacion_has_estado_vigencia_property(self):
        assert hasattr(Asignacion, "estado_vigencia")
        assert isinstance(Asignacion.__dict__["estado_vigencia"], property)

    def test_asignacion_has_id(self):
        assert hasattr(Asignacion, "id")

    def test_asignacion_has_tenant_id(self):
        assert hasattr(Asignacion, "tenant_id")

    def test_asignacion_has_deleted_at(self):
        assert hasattr(Asignacion, "deleted_at")

    def test_asignacion_usuario_id_fk(self):
        col = Asignacion.__mapper__.columns["usuario_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "users"

    def test_asignacion_responsable_id_fk(self):
        col = Asignacion.__mapper__.columns["responsable_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "users"

    def test_estado_vigencia_vigente(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now - timedelta(days=30),
            hasta=now + timedelta(days=30),
        )
        assert a.estado_vigencia == "Vigente"

    def test_estado_vigencia_vencida(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now - timedelta(days=60),
            hasta=now - timedelta(days=1),
        )
        assert a.estado_vigencia == "Vencida"

    def test_estado_vigencia_pendiente(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now + timedelta(days=1),
            hasta=now + timedelta(days=30),
        )
        assert a.estado_vigencia == "Pendiente"

    def test_estado_vigencia_vigente_sin_hasta(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now - timedelta(days=30),
            hasta=None,
        )
        assert a.estado_vigencia == "Vigente"
