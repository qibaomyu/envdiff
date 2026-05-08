"""Encrypt and decrypt environment variable values using Fernet symmetric encryption."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore


@dataclass
class EncryptResult:
    encrypted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Encrypted {len(self.encrypted)} key(s), "
            f"skipped {len(self.skipped)} key(s)."
        )


@dataclass
class DecryptResult:
    decrypted: Dict[str, str] = field(default_factory=dict)
    failed: List[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Decrypted {len(self.decrypted)} key(s), "
            f"failed {len(self.failed)} key(s)."
        )


def _require_cryptography() -> None:
    if Fernet is None:
        raise ImportError(
            "The 'cryptography' package is required for encryption. "
            "Install it with: pip install cryptography"
        )


def derive_key(passphrase: str) -> bytes:
    """Derive a Fernet-compatible key from a passphrase using SHA-256."""
    _require_cryptography()
    digest = hashlib.sha256(passphrase.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_env(
    env: Dict[str, str],
    keys: List[str],
    passphrase: str,
) -> EncryptResult:
    """Encrypt selected keys in an env dict. Returns EncryptResult."""
    _require_cryptography()
    fernet = Fernet(derive_key(passphrase))
    result = EncryptResult()
    for k, v in env.items():
        if k in keys:
            result.encrypted[k] = fernet.encrypt(v.encode()).decode()
        else:
            result.skipped.append(k)
    return result


def decrypt_env(
    env: Dict[str, str],
    passphrase: str,
) -> DecryptResult:
    """Attempt to decrypt all values in env dict. Returns DecryptResult."""
    _require_cryptography()
    fernet = Fernet(derive_key(passphrase))
    result = DecryptResult()
    for k, v in env.items():
        try:
            result.decrypted[k] = fernet.decrypt(v.encode()).decode()
        except (InvalidToken, Exception):
            result.failed.append(k)
    return result
