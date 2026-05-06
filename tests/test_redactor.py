"""Tests for envdiff.redactor."""

import pytest
from envdiff.redactor import (
    is_sensitive,
    redact_env,
    redact_value,
    REDACT_PLACEHOLDER,
    DEFAULT_SENSITIVE_PATTERNS,
)


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "AUTH_TOKEN": "tok_xyz",
        "DEBUG": "true",
        "SECRET_KEY": "supersecret",
        "PORT": "8080",
    }


def test_is_sensitive_password():
    assert is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_api_key():
    assert is_sensitive("API_KEY") is True


def test_is_sensitive_token():
    assert is_sensitive("AUTH_TOKEN") is True


def test_is_sensitive_secret():
    assert is_sensitive("SECRET_KEY") is True


def test_is_not_sensitive_plain_key():
    assert is_sensitive("APP_NAME") is False


def test_is_not_sensitive_port():
    assert is_sensitive("PORT") is False


def test_is_sensitive_case_insensitive():
    assert is_sensitive("db_password") is True


def test_is_sensitive_custom_patterns():
    assert is_sensitive("MY_CERT", patterns=[r".*CERT.*"]) is True
    assert is_sensitive("APP_NAME", patterns=[r".*CERT.*"]) is False


def test_redact_env_replaces_sensitive(sample_env):
    result = redact_env(sample_env)
    assert result["DB_PASSWORD"] == REDACT_PLACEHOLDER
    assert result["API_KEY"] == REDACT_PLACEHOLDER
    assert result["AUTH_TOKEN"] == REDACT_PLACEHOLDER
    assert result["SECRET_KEY"] == REDACT_PLACEHOLDER


def test_redact_env_preserves_safe_keys(sample_env):
    result = redact_env(sample_env)
    assert result["APP_NAME"] == "myapp"
    assert result["DEBUG"] == "true"
    assert result["PORT"] == "8080"


def test_redact_env_does_not_mutate_original(sample_env):
    original_password = sample_env["DB_PASSWORD"]
    redact_env(sample_env)
    assert sample_env["DB_PASSWORD"] == original_password


def test_redact_env_custom_placeholder(sample_env):
    result = redact_env(sample_env, placeholder="<hidden>")
    assert result["DB_PASSWORD"] == "<hidden>"


def test_redact_value_sensitive():
    assert redact_value("API_KEY", "abc123") == REDACT_PLACEHOLDER


def test_redact_value_not_sensitive():
    assert redact_value("APP_NAME", "myapp") == "myapp"


def test_redact_env_empty():
    assert redact_env({}) == {}
