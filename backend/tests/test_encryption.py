import base64

import pytest

from app.core.exceptions import EncryptionError
from app.core.security import decrypt, encrypt, is_encrypted


class TestEncryption:
    def test_encrypt_returns_string_with_prefix(self):
        result = encrypt("DNI 12345678")
        assert result.startswith("[cifrado]")

    def test_encrypt_output_is_valid_base64(self):
        result = encrypt("hello")
        payload = result[len("[cifrado]"):]
        base64.b64decode(payload)

    def test_encrypt_produces_different_ciphertexts(self):
        plaintext = "same data"
        r1 = encrypt(plaintext)
        r2 = encrypt(plaintext)
        assert r1 != r2

    def test_decrypt_round_trip(self):
        original = "DNI 12345678"
        encrypted = encrypt(original)
        decrypted = decrypt(encrypted)
        assert decrypted == original

    def test_decrypt_round_trip_special_chars(self):
        original = "abc123!@#$%^&*()_+ñöü"
        encrypted = encrypt(original)
        decrypted = decrypt(encrypted)
        assert decrypted == original

    def test_is_encrypted_true_for_cifrado_prefix(self):
        result = encrypt("test")
        assert is_encrypted(result) is True

    def test_is_encrypted_false_for_plaintext(self):
        assert is_encrypted("plain text") is False

    def test_is_encrypted_false_for_empty_string(self):
        assert is_encrypted("") is False

    def test_decrypt_invalid_ciphertext_raises_error(self):
        with pytest.raises(EncryptionError):
            decrypt("[cifrado]invalid-base64!!!")

    def test_decrypt_no_prefix_raises_error(self):
        with pytest.raises(EncryptionError):
            decrypt("plain text")

    def test_decrypt_error_does_not_expose_plaintext(self):
        with pytest.raises(EncryptionError) as excinfo:
            decrypt("[cifrado]AAAA")
        assert "AAAA" not in str(excinfo.value)

    def test_encrypt_empty_string(self):
        result = encrypt("")
        assert result.startswith("[cifrado]")
        assert decrypt(result) == ""

    def test_encrypt_long_string(self):
        original = "A" * 10000
        encrypted = encrypt(original)
        decrypted = decrypt(encrypted)
        assert decrypted == original

    def test_is_encrypted_prefix_only_no_ciphertext(self):
        assert is_encrypted("[cifrado]") is True

    def test_is_encrypted_case_sensitive(self):
        assert is_encrypted("[CIFRADO]data") is False
        assert is_encrypted("[Cifrado]data") is False
