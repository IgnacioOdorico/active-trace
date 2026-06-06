import base64
import os

from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.core.config import Settings
from app.core.exceptions import EncryptionError

_CIFRADO_PREFIX = "[cifrado]"
_settings = Settings()  # type: ignore[call-arg]


def _derive_key() -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"activia-trace-aes-256-cbc",
    )
    return hkdf.derive(_settings.ENCRYPTION_KEY.encode())


_KEY = _derive_key()


def encrypt(plaintext: str) -> str:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(_KEY), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    payload = iv + ciphertext
    return _CIFRADO_PREFIX + base64.b64encode(payload).decode()


def decrypt(ciphertext: str) -> str:
    if not ciphertext.startswith(_CIFRADO_PREFIX):
        raise EncryptionError("Invalid ciphertext format: missing prefix")
    try:
        raw = base64.b64decode(ciphertext[len(_CIFRADO_PREFIX):])
    except (ValueError, base64.binascii.Error) as exc:
        raise EncryptionError("Invalid ciphertext format: base64 decode failed") from exc
    if len(raw) < 16:
        raise EncryptionError("Invalid ciphertext format: too short")
    iv = raw[:16]
    ct = raw[16:]
    cipher = Cipher(algorithms.AES(_KEY), modes.CBC(iv))
    decryptor = cipher.decryptor()
    try:
        padded = decryptor.update(ct) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded) + unpadder.finalize()
    except Exception as exc:
        raise EncryptionError("Decryption failed") from exc
    return plaintext.decode()


def is_encrypted(value: str) -> bool:
    return value.startswith(_CIFRADO_PREFIX)
