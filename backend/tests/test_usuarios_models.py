from app.models.user import User


class TestUsuarioModel:
    def test_user_tablename(self):
        assert User.__tablename__ == "users"

    def test_user_has_nombre(self):
        assert hasattr(User, "nombre")

    def test_user_nombre_nullable(self):
        col = User.__mapper__.columns["nombre"]
        assert col.nullable

    def test_user_has_apellidos(self):
        assert hasattr(User, "apellidos")

    def test_user_has_dni(self):
        assert hasattr(User, "dni")

    def test_user_has_cuil(self):
        assert hasattr(User, "cuil")

    def test_user_has_cbu(self):
        assert hasattr(User, "cbu")

    def test_user_has_alias_cbu(self):
        assert hasattr(User, "alias_cbu")

    def test_user_has_banco(self):
        assert hasattr(User, "banco")

    def test_user_has_regional(self):
        assert hasattr(User, "regional")

    def test_user_has_legajo(self):
        assert hasattr(User, "legajo")

    def test_user_has_legajo_profesional(self):
        assert hasattr(User, "legajo_profesional")

    def test_user_has_facturador(self):
        assert hasattr(User, "facturador")

    def test_user_facturador_default_false(self):
        col = User.__mapper__.columns["facturador"]
        assert col.default is not None and col.default.arg is False

    def test_user_has_estado(self):
        assert hasattr(User, "estado")

    def test_user_estado_default_activo(self):
        col = User.__mapper__.columns["estado"]
        assert col.default is not None and col.default.arg == "Activo"

    def test_user_has_id(self):
        assert hasattr(User, "id")

    def test_user_has_tenant_id(self):
        assert hasattr(User, "tenant_id")

    def test_user_unique_email_per_tenant(self):
        found = any(
            c.name == "uq_user_email_per_tenant"
            for c in User.__table_args__
            if hasattr(c, "name")
        )
        assert found

    def test_user_hashed_password_nullable(self):
        col = User.__mapper__.columns["hashed_password"]
        assert col.nullable

    def test_user_email_type_string_500(self):
        col = User.__mapper__.columns["email"]
        assert col.type.length == 500
