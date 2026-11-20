import base64
import hashlib
import hmac
import json
import secrets
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def secret() -> str:
    return secrets.token_urlsafe(32)


def password_hash(password: str) -> str:
    if len(password) < 10 or len(password) > 1024:
        raise ValueError("Password must contain 10–1024 characters")
    salt = secrets.token_bytes(16)
    result = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
    return f"scrypt$16384$8$1${salt.hex()}${result.hex()}"


def password_verify(password: str, encoded: str) -> bool:
    try:
        _, n, r, p, salt, expected = encoded.split("$")
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p), dklen=32)
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False


def canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


class Crypto:
    def __init__(self, key: bytes, seed: bytes):
        self.aes = AESGCM(key)
        self.signer = Ed25519PrivateKey.from_private_bytes(seed)

    def encrypt(self, value: str) -> str:
        nonce = secrets.token_bytes(12)
        return base64.b64encode(nonce + self.aes.encrypt(nonce, value.encode(), b"kidsafe:v1")).decode()

    def decrypt(self, value: str) -> str:
        raw = base64.b64decode(value)
        return self.aes.decrypt(raw[:12], raw[12:], b"kidsafe:v1").decode()

    def envelope(self, payload: dict) -> dict:
        return {"payload": payload, "signature": base64.b64encode(self.signer.sign(canonical(payload))).decode(),
                "public_key": base64.b64encode(self.signer.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()}
