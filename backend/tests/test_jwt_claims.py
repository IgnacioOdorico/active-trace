from app.core.auth import create_access_token, decode_access_token


class TestJwtRolsClaim:
    def test_token_contains_rols(self):
        token = create_access_token(user_id="u1", tenant_id="t1", roles=["ADMIN", "PROFESOR"])
        payload = decode_access_token(token)
        assert payload.get("rols") == ["ADMIN", "PROFESOR"]

    def test_token_without_roles_defaults_empty(self):
        token = create_access_token(user_id="u1", tenant_id="t1")
        payload = decode_access_token(token)
        assert payload.get("rols") == []

    def test_token_with_single_role(self):
        token = create_access_token(user_id="u1", tenant_id="t1", roles=["TUTOR"])
        payload = decode_access_token(token)
        assert payload.get("rols") == ["TUTOR"]

    def test_token_rols_not_roles_key(self):
        token = create_access_token(user_id="u1", tenant_id="t1", roles=["ADMIN"])
        payload = decode_access_token(token)
        assert "roles" not in payload
        assert "rols" in payload
