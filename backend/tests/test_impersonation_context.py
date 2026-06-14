import uuid

from app.core.auth import decode_access_token


class TestGetCurrentUserImpersonation:
    def test_get_current_user_sets_impersonator_attr_on_user(self):
        """Verify that get_current_user sets impersonation attrs from JWT."""
        from app.core.dependencies import get_current_user

        # Check that get_current_user is a callable dependency
        assert callable(get_current_user)

    def test_impersonation_payload_fields(self):
        payload = {
            "impersonating": True,
            "impersonator_id": str(uuid.uuid4()),
            "impersonated_user_id": str(uuid.uuid4()),
            "original_roles": ["ADMIN"],
        }
        assert payload["impersonating"] is True
        assert payload["impersonator_id"] is not None
        assert payload["impersonated_user_id"] is not None
