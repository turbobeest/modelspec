"""A ModelSpec key in the environment or a private user configuration file."""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .errors import ClientError

KEY_ENV = "MODELSPEC_API_KEY"


def config_dir() -> Path:
    if value := os.environ.get("XDG_CONFIG_HOME"):
        return Path(value).expanduser() / "modelspec"
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", str(Path.home() / "AppData/Roaming"))) / "modelspec"
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/modelspec"
    return Path.home() / ".config/modelspec"


def key_path() -> Path:
    return config_dir() / "api-key"


def valid_key(value: str) -> bool:
    return 0 < len(value) <= 4096 and all(33 <= ord(char) <= 126 for char in value)


@dataclass(frozen=True)
class Credential:
    secret: str = field(repr=False)

    def redact(self, text: str) -> str:
        escaped = json.dumps(self.secret)[1:-1]
        return text.replace(escaped, "[redacted]").replace(self.secret, "[redacted]")


def require_key() -> Credential:
    if KEY_ENV in os.environ:
        value = os.environ[KEY_ENV].strip()
    else:
        path = key_path()
        try:
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
                metadata = os.fstat(stream.fileno())
                if not stat.S_ISREG(metadata.st_mode) or (
                    os.name != "nt" and stat.S_IMODE(metadata.st_mode) != 0o600
                ):
                    raise ClientError("auth_unreadable", recovery="key", exit_code=5)
                value = stream.read(4098).strip()
        except FileNotFoundError:
            raise ClientError("missing_api_key", recovery="key", exit_code=5) from None
        except (OSError, UnicodeError):
            raise ClientError("auth_unreadable", recovery="key", exit_code=5) from None
    if not value:
        raise ClientError("missing_api_key", recovery="key", exit_code=5)
    if not valid_key(value):
        raise ClientError("invalid_api_key", recovery="key", exit_code=5)
    return Credential(value)


def store_key(value: str) -> Path:
    value = value.strip()
    if not valid_key(value):
        raise ClientError("invalid_api_key", recovery="key", exit_code=5)
    path = key_path()
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if path.is_symlink():
            raise ClientError("auth_unwritable", recovery="key")
        descriptor, name = tempfile.mkstemp(prefix=".api-key-", dir=path.parent)
        temporary = Path(name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            if hasattr(os, "fchmod"):
                try:
                    os.fchmod(stream.fileno(), 0o600)
                except (OSError, NotImplementedError):
                    if os.name != "nt":
                        raise
            stream.write(value + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    except OSError:
        raise ClientError("auth_unwritable", recovery="key") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path
