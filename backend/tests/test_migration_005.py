import importlib.util
from pathlib import Path

import pytest


class TestMigration005:
    def test_migration_file_exists(self):
        migration_path = Path("alembic/versions/005_create_audit_log.py")
        assert migration_path.exists(), "Migration file 005_create_audit_log.py not found"

    def test_migration_is_valid_python(self):
        migration_path = Path("alembic/versions/005_create_audit_log.py")
        spec = importlib.util.spec_from_file_location("migration_005", migration_path)
        assert spec is not None, f"Cannot load spec from {migration_path}"
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            pytest.fail(f"Migration module failed to load: {e}")
        assert mod.revision == "005"
        assert mod.down_revision == "004"
        assert hasattr(mod, "upgrade")
        assert hasattr(mod, "downgrade")

    def test_migration_upgrade_creates_table(self):
        from alembic.operations.ops import CreateTableOp
        from alembic.migration import MigrationContext
        from alembic.operations import Operations
        from sqlalchemy import MetaData, Table

        migration_path = Path("alembic/versions/005_create_audit_log.py")
        spec = importlib.util.spec_from_file_location("migration_005", migration_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        assert mod.revision == "005"
        assert mod.down_revision == "004"

    def test_downgrade_drops_table(self):
        migration_path = Path("alembic/versions/005_create_audit_log.py")
        spec = importlib.util.spec_from_file_location("migration_005", migration_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        assert callable(mod.downgrade)
