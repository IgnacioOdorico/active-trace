import uuid

from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.user_rol import UserRol


class TestRolModel:
    def test_rol_tablename(self):
        assert Rol.__tablename__ == "roles"

    def test_rol_has_codigo(self):
        assert hasattr(Rol, "codigo")

    def test_rol_codigo_unique(self):
        col = Rol.__mapper__.columns["codigo"]
        assert col.unique

    def test_rol_has_nombre(self):
        assert hasattr(Rol, "nombre")

    def test_rol_has_descripcion(self):
        assert hasattr(Rol, "descripcion")

    def test_rol_descripcion_nullable(self):
        col = Rol.__mapper__.columns["descripcion"]
        assert col.nullable

    def test_rol_has_activo(self):
        assert hasattr(Rol, "activo")

    def test_rol_activo_default_true(self):
        col = Rol.__mapper__.columns["activo"]
        assert col.default is not None and col.default.arg is True

    def test_rol_has_id(self):
        assert hasattr(Rol, "id")

    def test_rol_has_created_at(self):
        assert hasattr(Rol, "created_at")

    def test_rol_has_updated_at(self):
        assert hasattr(Rol, "updated_at")

    def test_rol_has_deleted_at(self):
        assert hasattr(Rol, "deleted_at")

    def test_rol_has_permisos_relationship(self):
        assert hasattr(Rol, "permisos")

    def test_rol_creates_with_basic_fields(self):
        rol = Rol(codigo="TEST", nombre="Test Role", descripcion="A test role")
        assert rol.codigo == "TEST"
        assert rol.nombre == "Test Role"
        assert rol.descripcion == "A test role"

    def test_rol_creates_without_descripcion(self):
        rol = Rol(codigo="MIN", nombre="Minimal")
        assert rol.descripcion is None


class TestPermisoModel:
    def test_permiso_tablename(self):
        assert Permiso.__tablename__ == "permisos"

    def test_permiso_has_codigo(self):
        assert hasattr(Permiso, "codigo")

    def test_permiso_codigo_unique(self):
        col = Permiso.__mapper__.columns["codigo"]
        assert col.unique

    def test_permiso_has_nombre(self):
        assert hasattr(Permiso, "nombre")

    def test_permiso_has_descripcion(self):
        assert hasattr(Permiso, "descripcion")

    def test_permiso_descripcion_nullable(self):
        col = Permiso.__mapper__.columns["descripcion"]
        assert col.nullable

    def test_permiso_has_modulo(self):
        assert hasattr(Permiso, "modulo")

    def test_permiso_has_propio(self):
        assert hasattr(Permiso, "propio")

    def test_permiso_propio_default_false(self):
        col = Permiso.__mapper__.columns["propio"]
        assert col.default is not None and col.default.arg is False

    def test_permiso_has_roles_relationship(self):
        assert hasattr(Permiso, "roles")

    def test_permiso_creates_with_codigo_modulo_accion(self):
        perm = Permiso(codigo="equipos:asignar", nombre="Asignar equipos", modulo="equipos")
        assert perm.codigo == "equipos:asignar"
        assert perm.modulo == "equipos"

    def test_permiso_with_propio_flag(self):
        perm = Permiso(codigo="atrasados:ver", nombre="Ver atrasados", modulo="atrasados", propio=True)
        assert perm.propio is True

    def test_permiso_wildcard_codigo(self):
        perm = Permiso(codigo="liquidaciones:*", nombre="Todo liquidaciones", modulo="liquidaciones")
        assert perm.codigo == "liquidaciones:*"


class TestRolPermisoModel:
    def test_rol_permiso_tablename(self):
        assert RolPermiso.__tablename__ == "rol_permisos"

    def test_rol_permiso_has_rol_id(self):
        assert hasattr(RolPermiso, "rol_id")

    def test_rol_permiso_has_permiso_id(self):
        assert hasattr(RolPermiso, "permiso_id")

    def test_rol_permiso_has_ambito(self):
        assert hasattr(RolPermiso, "ambito")

    def test_rol_permiso_ambito_nullable(self):
        col = RolPermiso.__mapper__.columns["ambito"]
        assert col.nullable

    def test_rol_permiso_unique_constraint(self):
        found = any(
            c.name == "uq_rol_permiso"
            for c in RolPermiso.__table_args__
            if hasattr(c, "name")
        )
        assert found


class TestUserRolModel:
    def test_user_rol_tablename(self):
        assert UserRol.__tablename__ == "user_roles"

    def test_user_rol_has_user_id(self):
        assert hasattr(UserRol, "user_id")

    def test_user_rol_has_rol_id(self):
        assert hasattr(UserRol, "rol_id")

    def test_user_rol_unique_constraint(self):
        found = any(
            c.name == "uq_user_rol"
            for c in UserRol.__table_args__
            if hasattr(c, "name")
        )
        assert found

    def test_user_rol_creates(self):
        uid = uuid.uuid4()
        rid = uuid.uuid4()
        ur = UserRol(user_id=uid, rol_id=rid)
        assert ur.user_id == uid
        assert ur.rol_id == rid
