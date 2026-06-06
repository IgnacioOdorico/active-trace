import uuid
from datetime import datetime

from app.models.refresh_token import RefreshToken
from app.models.recovery_token import RecoveryToken
from app.models.user import User

from app.models.base import EntityMeta


class TestUserModel:
    def test_user_tablename(self):
        assert User.__tablename__ == "users"

    def test_user_inherits_entity_meta(self):
        assert issubclass(User, EntityMeta)

    def test_user_has_email_column(self):
        assert hasattr(User, "email")

    def test_user_has_hashed_password_column(self):
        assert hasattr(User, "hashed_password")

    def test_user_has_is_active_column(self):
        assert hasattr(User, "is_active")

    def test_user_has_totp_secret_column(self):
        assert hasattr(User, "totp_secret")

    def test_user_totp_secret_nullable(self):
        col = User.__mapper__.columns["totp_secret"]
        assert col.nullable

    def test_user_has_totp_enabled_column(self):
        assert hasattr(User, "totp_enabled")

    def test_user_totp_enabled_default_false(self):
        col = User.__mapper__.columns["totp_enabled"]
        assert col.default is not None and col.default.arg is False

    def test_user_is_active_default_true(self):
        col = User.__mapper__.columns["is_active"]
        assert col.default is not None and col.default.arg is True

    def test_user_has_tenant_id(self):
        assert hasattr(User, "tenant_id")

    def test_user_has_id(self):
        assert hasattr(User, "id")

    def test_user_has_created_at(self):
        assert hasattr(User, "created_at")

    def test_user_has_updated_at(self):
        assert hasattr(User, "updated_at")

    def test_user_has_deleted_at(self):
        assert hasattr(User, "deleted_at")

    def test_user_creates_with_basic_fields(self):
        uid = uuid.uuid4()
        user = User(email="test@example.com", hashed_password="hash", tenant_id=uid)
        assert user.email == "test@example.com"
        assert user.hashed_password == "hash"
        assert user.tenant_id == uid
        assert user.totp_secret is None


class TestRefreshTokenModel:
    def test_refresh_token_tablename(self):
        assert RefreshToken.__tablename__ == "refresh_tokens"

    def test_refresh_token_inherits_entity_meta(self):
        assert issubclass(RefreshToken, EntityMeta)

    def test_refresh_token_has_token_hash(self):
        assert hasattr(RefreshToken, "token_hash")

    def test_refresh_token_token_hash_unique(self):
        col = RefreshToken.__mapper__.columns["token_hash"]
        assert col.unique

    def test_refresh_token_has_user_id(self):
        assert hasattr(RefreshToken, "user_id")

    def test_refresh_token_has_expires_at(self):
        assert hasattr(RefreshToken, "expires_at")

    def test_refresh_token_has_revoked(self):
        assert hasattr(RefreshToken, "revoked")

    def test_refresh_token_revoked_default_false(self):
        col = RefreshToken.__mapper__.columns["revoked"]
        assert col.default is not None and col.default.arg is False

    def test_refresh_token_has_replaced_by_token_hash(self):
        assert hasattr(RefreshToken, "replaced_by_token_hash")

    def test_refresh_token_replaced_by_token_hash_nullable(self):
        col = RefreshToken.__mapper__.columns["replaced_by_token_hash"]
        assert col.nullable

    def test_refresh_token_has_tenant_id(self):
        assert hasattr(RefreshToken, "tenant_id")

    def test_refresh_token_creates_with_fields(self):
        uid = uuid.uuid4()
        tid = uuid.uuid4()
        token = RefreshToken(
            token_hash="abc123",
            user_id=uid,
            tenant_id=tid,
            expires_at=datetime.now(),
        )
        assert token.token_hash == "abc123"
        assert token.user_id == uid
        assert token.tenant_id == tid
        assert token.replaced_by_token_hash is None


class TestRecoveryTokenModel:
    def test_recovery_token_tablename(self):
        assert RecoveryToken.__tablename__ == "recovery_tokens"

    def test_recovery_token_has_token_hash(self):
        assert hasattr(RecoveryToken, "token_hash")

    def test_recovery_token_token_hash_unique(self):
        col = RecoveryToken.__mapper__.columns["token_hash"]
        assert col.unique

    def test_recovery_token_has_user_id(self):
        assert hasattr(RecoveryToken, "user_id")

    def test_recovery_token_has_expires_at(self):
        assert hasattr(RecoveryToken, "expires_at")

    def test_recovery_token_has_used(self):
        assert hasattr(RecoveryToken, "used")

    def test_recovery_token_used_default_false(self):
        col = RecoveryToken.__mapper__.columns["used"]
        assert col.default is not None and col.default.arg is False

    def test_recovery_token_has_created_at(self):
        assert hasattr(RecoveryToken, "created_at")

    def test_recovery_token_has_id(self):
        assert hasattr(RecoveryToken, "id")

    def test_recovery_token_creates_with_fields(self):
        uid = uuid.uuid4()
        token = RecoveryToken(
            token_hash="def456",
            user_id=uid,
            expires_at=datetime.now(),
        )
        assert token.token_hash == "def456"
        assert token.user_id == uid
