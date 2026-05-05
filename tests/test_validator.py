"""Tests for envdiff.validator module."""

import pytest
from envdiff.validator import validate_env, ValidationIssue, ValidationResult


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_HOST": "localhost",
        "SECRET_KEY": "abc123",
        "EMPTY_VAR": "",
    }


def test_valid_env_no_issues(sample_env):
    result = validate_env(sample_env)
    assert not result.has_errors
    assert not result.has_warnings
    assert result.issues == []


def test_invalid_key_detected():
    env = {"VALID_KEY": "ok", "123INVALID": "bad", "also-bad": "nope"}
    result = validate_env(env)
    invalid_keys = {i.key for i in result.issues}
    assert "123INVALID" in invalid_keys
    assert "also-bad" in invalid_keys
    assert "VALID_KEY" not in invalid_keys


def test_required_keys_missing(sample_env):
    result = validate_env(sample_env, required_keys=["APP_NAME", "MISSING_KEY"])
    assert result.has_errors
    keys = {i.key for i in result.errors()}
    assert "MISSING_KEY" in keys
    assert "APP_NAME" not in keys


def test_required_keys_all_present(sample_env):
    result = validate_env(sample_env, required_keys=["APP_NAME", "DB_HOST"])
    assert not result.has_errors


def test_forbidden_keys_present(sample_env):
    result = validate_env(sample_env, forbidden_keys=["SECRET_KEY"])
    assert result.has_errors
    assert any(i.key == "SECRET_KEY" for i in result.errors())


def test_forbidden_keys_absent(sample_env):
    result = validate_env(sample_env, forbidden_keys=["NOT_PRESENT"])
    assert not result.has_errors


def test_empty_values_warning(sample_env):
    result = validate_env(sample_env, no_empty_values=True)
    assert result.has_warnings
    assert any(i.key == "EMPTY_VAR" for i in result.warnings())


def test_empty_values_not_flagged_by_default(sample_env):
    result = validate_env(sample_env)
    assert not result.has_warnings


def test_combined_rules():
    env = {"APP": "ok", "EMPTY": "", "BAD KEY": "x"}
    result = validate_env(
        env,
        required_keys=["MISSING"],
        forbidden_keys=["APP"],
        no_empty_values=True,
    )
    keys = {i.key for i in result.issues}
    assert "MISSING" in keys
    assert "APP" in keys
    assert "EMPTY" in keys
    assert "BAD KEY" in keys


def test_validation_result_errors_and_warnings():
    result = ValidationResult()
    result.issues.append(ValidationIssue("K1", "err msg", "error"))
    result.issues.append(ValidationIssue("K2", "warn msg", "warning"))
    assert result.has_errors
    assert result.has_warnings
    assert len(result.errors()) == 1
    assert len(result.warnings()) == 1
