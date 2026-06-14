from app.core.auth import create_access_token, decode_access_token


class TestImpersonationJWT:
    def test_normal_token_has_impersonating_false(self):
        token = create_access_token(user_id="u1", tenant_id="t1", roles=["ADMIN"])
        payload = decode_access_token(token)
        assert payload.get("impersonating") is False

    def test_normal_token_no_impersonation_fields(self):
        token = create_access_token(user_id="u1", tenant_id="t1")
        payload = decode_access_token(token)
        assert "impersonator_id" not in payload
        assert "impersonated_user_id" not in payload
        assert "original_roles" not in payload

    def test_impersonation_token_has_all_fields(self):
        token = create_access_token(
            user_id="u1",
            tenant_id="t1",
            roles=["ADMIN"],
            impersonating=True,
            impersonator_id="admin-user",
            impersonated_user_id="target-user",
            original_roles=["ADMIN"],
        )
        payload = decode_access_token(token)
        assert payload.get("impersonating") is True
        assert payload.get("impersonator_id") == "admin-user"
        assert payload.get("impersonated_user_id") == "target-user"
        assert payload.get("original_roles") == ["ADMIN"]

    def test_impersonation_token_preserves_tenant(self):
        token = create_access_token(
            user_id="u1",
            tenant_id="t1",
            roles=["ADMIN"],
            impersonating=True,
            impersonator_id="admin-user",
            impersonated_user_id="target-user",
            original_roles=["ADMIN"],
        )
        payload = decode_access_token(token)
        assert payload["tenant_id"] == "t1"
        assert payload["sub"] == "u1"
