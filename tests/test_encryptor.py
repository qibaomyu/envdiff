"""Tests for envdiff.encryptor."""

import pytest

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

pytestmark = pytest.mark.skipif(
    not HAS_CRYPTOGRAPHY,
    reason="cryptography package not installed",
)

from envdiff.encryptor import (
    derive_key,
    encrypt_env,
    decrypt_env,
    EncryptResult,
    DecryptResult,
)

PASSPHRASE = "supersecret"


@pytest.fixture
def sample_env():
    return {
        "DB_PASSWORD": "hunter2",
        "API_KEY": "abc123",
        "APP_NAME": "envdiff",
    }


def test_derive_key_returns_bytes():
    key = derive_key(PASSPHRASE)
    assert isinstance(key, bytes)
    assert len(key) == 44  # base64-encoded 32 bytes


def test_derive_key_deterministic():
    assert derive_key(PASSPHRASE) == derive_key(PASSPHRASE)


def test_derive_key_different_passphrases():
    assert derive_key("one") != derive_key("two")


def test_encrypt_env_returns_encrypt_result(sample_env):
    result = encrypt_env(sample_env, ["DB_PASSWORD", "API_KEY"], PASSPHRASE)
    assert isinstance(result, EncryptResult)


def test_encrypt_env_encrypts_selected_keys(sample_env):
    result = encrypt_env(sample_env, ["DB_PASSWORD"], PASSPHRASE)
    assert "DB_PASSWORD" in result.encrypted
    assert result.encrypted["DB_PASSWORD"] != "hunter2"


def test_encrypt_env_skips_non_selected_keys(sample_env):
    result = encrypt_env(sample_env, ["DB_PASSWORD"], PASSPHRASE)
    assert "APP_NAME" in result.skipped
    assert "API_KEY" in result.skipped


def test_encrypt_env_summary(sample_env):
    result = encrypt_env(sample_env, ["DB_PASSWORD", "API_KEY"], PASSPHRASE)
    summary = result.summary()
    assert "2" in summary
    assert "1" in summary


def test_decrypt_env_roundtrip(sample_env):
    keys = ["DB_PASSWORD", "API_KEY"]
    encrypted = encrypt_env(sample_env, keys, PASSPHRASE)
    # Build an env of only encrypted values
    enc_env = dict(encrypted.encrypted)
    decrypted = decrypt_env(enc_env, PASSPHRASE)
    assert decrypted.decrypted["DB_PASSWORD"] == "hunter2"
    assert decrypted.decrypted["API_KEY"] == "abc123"


def test_decrypt_env_wrong_passphrase(sample_env):
    keys = ["DB_PASSWORD"]
    encrypted = encrypt_env(sample_env, keys, PASSPHRASE)
    enc_env = dict(encrypted.encrypted)
    result = decrypt_env(enc_env, "wrongpassphrase")
    assert "DB_PASSWORD" in result.failed
    assert result.decrypted == {}


def test_decrypt_env_returns_decrypt_result(sample_env):
    result = decrypt_env({}, PASSPHRASE)
    assert isinstance(result, DecryptResult)


def test_decrypt_env_summary():
    result = DecryptResult(decrypted={"A": "1"}, failed=["B"])
    assert "1" in result.summary()
    assert "1" in result.summary()
