class TestProgramaMateriaModel:
    def test_tablename(self):
        from app.models.programa_materia import ProgramaMateria
        assert ProgramaMateria.__tablename__ == "programa_materia"

    def test_has_entity_meta_fields(self):
        from app.models.programa_materia import ProgramaMateria
        assert hasattr(ProgramaMateria, "id")
        assert hasattr(ProgramaMateria, "tenant_id")
        assert hasattr(ProgramaMateria, "created_at")
        assert hasattr(ProgramaMateria, "updated_at")
        assert hasattr(ProgramaMateria, "deleted_at")

    def test_has_programa_fields(self):
        from app.models.programa_materia import ProgramaMateria
        assert hasattr(ProgramaMateria, "materia_id")
        assert hasattr(ProgramaMateria, "carrera_id")
        assert hasattr(ProgramaMateria, "cohorte_id")
        assert hasattr(ProgramaMateria, "titulo")
        assert hasattr(ProgramaMateria, "referencia_archivo")
        assert hasattr(ProgramaMateria, "cargado_at")

    def test_titulo_string_200(self):
        from app.models.programa_materia import ProgramaMateria
        col = ProgramaMateria.__mapper__.columns["titulo"]
        assert col.type.length == 200
        assert col.nullable is False

    def test_referencia_archivo_string_500(self):
        from app.models.programa_materia import ProgramaMateria
        col = ProgramaMateria.__mapper__.columns["referencia_archivo"]
        assert col.type.length == 500
        assert col.nullable is False

    def test_materia_id_fk(self):
        from app.models.programa_materia import ProgramaMateria
        col = ProgramaMateria.__mapper__.columns["materia_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "materias"

    def test_carrera_id_fk(self):
        from app.models.programa_materia import ProgramaMateria
        col = ProgramaMateria.__mapper__.columns["carrera_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "carreras"

    def test_cohorte_id_fk(self):
        from app.models.programa_materia import ProgramaMateria
        col = ProgramaMateria.__mapper__.columns["cohorte_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "cohortes"

    def test_cargado_at_not_nullable(self):
        from app.models.programa_materia import ProgramaMateria
        col = ProgramaMateria.__mapper__.columns["cargado_at"]
        assert col.nullable is False


class TestTipoFechaAcademica:
    def test_enum_values(self):
        from app.models.fecha_academica import TipoFechaAcademica
        assert TipoFechaAcademica.PARCIAL.value == "Parcial"
        assert TipoFechaAcademica.TP.value == "TP"
        assert TipoFechaAcademica.COLOQUIO.value == "Coloquio"
        assert TipoFechaAcademica.RECUPERATORIO.value == "Recuperatorio"

    def test_enum_all_members_present(self):
        from app.models.fecha_academica import TipoFechaAcademica
        expected = {"Parcial", "TP", "Coloquio", "Recuperatorio"}
        actual = {m.value for m in TipoFechaAcademica}
        assert actual == expected


class TestFechaAcademicaModel:
    def test_tablename(self):
        from app.models.fecha_academica import FechaAcademica
        assert FechaAcademica.__tablename__ == "fecha_academica"

    def test_has_entity_meta_fields(self):
        from app.models.fecha_academica import FechaAcademica
        assert hasattr(FechaAcademica, "id")
        assert hasattr(FechaAcademica, "tenant_id")
        assert hasattr(FechaAcademica, "created_at")
        assert hasattr(FechaAcademica, "updated_at")
        assert hasattr(FechaAcademica, "deleted_at")

    def test_has_fecha_fields(self):
        from app.models.fecha_academica import FechaAcademica
        assert hasattr(FechaAcademica, "materia_id")
        assert hasattr(FechaAcademica, "cohorte_id")
        assert hasattr(FechaAcademica, "tipo")
        assert hasattr(FechaAcademica, "numero")
        assert hasattr(FechaAcademica, "periodo")
        assert hasattr(FechaAcademica, "fecha")
        assert hasattr(FechaAcademica, "titulo")

    def test_tipo_string_20(self):
        from app.models.fecha_academica import FechaAcademica
        col = FechaAcademica.__mapper__.columns["tipo"]
        assert col.type.length == 20
        assert col.nullable is False

    def test_titulo_string_200(self):
        from app.models.fecha_academica import FechaAcademica
        col = FechaAcademica.__mapper__.columns["titulo"]
        assert col.type.length == 200
        assert col.nullable is False

    def test_materia_id_fk(self):
        from app.models.fecha_academica import FechaAcademica
        col = FechaAcademica.__mapper__.columns["materia_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "materias"

    def test_cohorte_id_fk(self):
        from app.models.fecha_academica import FechaAcademica
        col = FechaAcademica.__mapper__.columns["cohorte_id"]
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "cohortes"
