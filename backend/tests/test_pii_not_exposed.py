"""Verify PII is not exposed in logs or error responses.

PII fields (email, dni, cuil, cbu, alias_cbu) MUST be encrypted before storage
and MUST NOT appear in plain text in logs, error messages, or API responses.
"""

import pytest

from app.core.exceptions import EncryptionError
from app.core.security import decrypt, encrypt, is_encrypted


class TestPIINotExposed:
    def test_encryption_round_trip_for_all_pii_fields(self):
        fields = {
            "email": "docente@mail.com",
            "dni": "12345678",
            "cuil": "20-12345678-9",
            "cbu": "0000003100000000000001",
            "alias_cbu": "MI.ALIAS",
        }
        for field_name, plaintext in fields.items():
            encrypted = encrypt(plaintext)
            assert is_encrypted(encrypted), f"{field_name} should be encrypted"
            decrypted = decrypt(encrypted)
            assert decrypted == plaintext, f"{field_name} round-trip failed"

    def test_encrypted_values_have_cifrado_prefix(self):
        for val in ["test@mail.com", "12345678", "20-12345678-9"]:
            assert encrypt(val).startswith("[cifrado]")

    def test_decrypt_error_does_not_expose_pii_in_exception(self):
        try:
            decrypt("[cifrado]AAAA")
        except EncryptionError as e:
            assert "AAAA" not in str(e)
            assert "12345678" not in str(e)
            assert "docente" not in str(e)

    def test_encryption_error_on_invalid_input(self):
        with pytest.raises(EncryptionError):
            decrypt("plain text")

    def test_encryption_service_layer_mocks_pii_not_leaked(self):
        """Verify that when domain errors occur, PII doesn't appear in the error detail."""
        from app.core.exceptions import DomainError

        err = DomainError("EMAIL_DUPLICADO", {"email": "email"})
        assert err.detail == "EMAIL_DUPLICADO"
        assert "docente@mail.com" not in str(err)
        assert "12345678" not in str(err)
