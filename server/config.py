from dataclasses import dataclass
import base64
import os


@dataclass
class Settings:
    database_url: str
    encryption_key: bytes
    signing_seed: bytes
    secure_cookie: bool = True
    allowed_hosts: tuple[str, ...] = ("localhost", "127.0.0.1", "testserver")

    @classmethod
    def from_env(cls):
        def key(name):
            value = base64.b64decode(os.environ[name], validate=True)
            if len(value) != 32:
                raise ValueError(f"{name} must decode to 32 bytes")
            return value
        return cls(os.getenv("KIDSAFE_DATABASE_URL", "sqlite:///./.runtime/kidsafe.db"),
                   key("KIDSAFE_ENCRYPTION_KEY"), key("KIDSAFE_SIGNING_SEED"),
                   allowed_hosts=tuple(os.getenv("KIDSAFE_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")))
