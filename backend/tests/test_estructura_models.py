from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia


class TestCarreraModel:
    def test_carrera_tablename(self):
        assert Carrera.__tablename__ == "carreras"

    def test_carrera_has_codigo(self):
        assert hasattr(Carrera, "codigo")

    def test_carrera_has_nombre(self):
        assert hasattr(Carrera, "nombre")

    def test_carrera_has_descripcion(self):
        assert hasattr(Carrera, "descripcion")

    def test_carrera_descripcion_nullable(self):
        col = Carrera.__mapper__.columns["descripcion"]
        assert col.nullable

    def test_carrera_has_activa(self):
        assert hasattr(Carrera, "activa")

    def test_carrera_activa_default_true(self):
        col = Carrera.__mapper__.columns["activa"]
        assert col.default is not None and col.default.arg is True

    def test_carrera_has_id(self):
        assert hasattr(Carrera, "id")

    def test_carrera_has_tenant_id(self):
        assert hasattr(Carrera, "tenant_id")

    def test_carrera_has_created_at(self):
        assert hasattr(Carrera, "created_at")

    def test_carrera_has_updated_at(self):
        assert hasattr(Carrera, "updated_at")

    def test_carrera_has_deleted_at(self):
        assert hasattr(Carrera, "deleted_at")

    def test_carrera_has_cohortes_relationship(self):
        assert hasattr(Carrera, "cohortes")

    def test_carrera_has_materias_relationship(self):
        assert hasattr(Carrera, "materias")

    def test_carrera_unique_constraint(self):
        found = any(
            c.name == "uq_carrera_codigo_tenant"
            for c in Carrera.__table_args__
            if hasattr(c, "name")
        )
        assert found


class TestCohorteModel:
    def test_cohorte_tablename(self):
        assert Cohorte.__tablename__ == "cohortes"

    def test_cohorte_has_nombre(self):
        assert hasattr(Cohorte, "nombre")

    def test_cohorte_has_carrera_id(self):
        assert hasattr(Cohorte, "carrera_id")

    def test_cohorte_has_fecha_inicio(self):
        assert hasattr(Cohorte, "fecha_inicio")

    def test_cohorte_has_fecha_fin(self):
        assert hasattr(Cohorte, "fecha_fin")

    def test_cohorte_has_activa(self):
        assert hasattr(Cohorte, "activa")

    def test_cohorte_activa_default_true(self):
        col = Cohorte.__mapper__.columns["activa"]
        assert col.default is not None and col.default.arg is True

    def test_cohorte_has_id(self):
        assert hasattr(Cohorte, "id")

    def test_cohorte_has_tenant_id(self):
        assert hasattr(Cohorte, "tenant_id")

    def test_cohorte_has_carrera_relationship(self):
        assert hasattr(Cohorte, "carrera")

    def test_cohorte_carrera_id_fk(self):
        col = Cohorte.__mapper__.columns["carrera_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "carreras"

    def test_cohorte_unique_constraint(self):
        found = any(
            c.name == "uq_cohorte_nombre_carrera_tenant"
            for c in Cohorte.__table_args__
            if hasattr(c, "name")
        )
        assert found


class TestMateriaModel:
    def test_materia_tablename(self):
        assert Materia.__tablename__ == "materias"

    def test_materia_has_codigo(self):
        assert hasattr(Materia, "codigo")

    def test_materia_has_nombre(self):
        assert hasattr(Materia, "nombre")

    def test_materia_has_descripcion(self):
        assert hasattr(Materia, "descripcion")

    def test_materia_descripcion_nullable(self):
        col = Materia.__mapper__.columns["descripcion"]
        assert col.nullable

    def test_materia_has_carrera_id(self):
        assert hasattr(Materia, "carrera_id")

    def test_materia_carrera_id_nullable(self):
        col = Materia.__mapper__.columns["carrera_id"]
        assert col.nullable

    def test_materia_has_id(self):
        assert hasattr(Materia, "id")

    def test_materia_has_tenant_id(self):
        assert hasattr(Materia, "tenant_id")

    def test_materia_has_carrera_relationship(self):
        assert hasattr(Materia, "carrera")

    def test_materia_carrera_id_fk(self):
        col = Materia.__mapper__.columns["carrera_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "carreras"

    def test_materia_unique_constraint(self):
        found = any(
            c.name == "uq_materia_codigo_tenant"
            for c in Materia.__table_args__
            if hasattr(c, "name")
        )
        assert found
