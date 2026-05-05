"""Edge-case tests for envdiff.validator."""

import pytest
from envdiff.validator import validate_env, ValidationResult, ValidationIssue


def test_empty_env_no_issues():
    result = validate_env({})
    assert result.issues == []
    assert not result.has_errors
    assert not result.has_warnings


def test_required_keys_empty_list():
    env = {"A": "1"}
    result = validate_env(env, required_keys=[])
    assert not result.has_errors


def test_forbidden_keys_empty_list():
    env = {"A": "1"}
    result = validate_env(env, forbidden_keys=[])
    assert not result.has_errors


def test_key_with_leading_underscore_is_valid():
    env = {"_PRIVATE": "secret"}
    result = validate_env(env)
    assert not result.has_errors


def test_key_with_numbers_is_valid():
    env = {"VAR_123": "value"}
    result = validate_env(env)
    assert not result.has_errors


def test_key_starting_with_number_is_invalid():
    env = {"1BAD": "value"}
    result = validate_env(env)
    assert result.has_errors
    assert result.errors()[0].key == "1BAD"


def test_key_with_space_is_invalid():
    env = {"BAD KEY": "value"}
    result = validate_env(env)
    assert result.has_errors


def test_key_with_hyphen_is_invalid():
    env = {"BAD-KEY": "value"}
    result = validate_env(env)
    assert result.has_errors


def test_multiple_issues_accumulated():
    env = {"OK": "fine", "1BAD": "x", "EMPTY": ""}
    result = validate_env(
        env,
        required_keys=["MISSING"],
        no_empty_values=True,
    )
    keys = {i.key for i in result.issues}
    assert "1BAD" in keys
    assert "MISSING" in keys
    assert "EMPTY" in keys


def test_validation_issue_repr():
    issue = ValidationIssue("MY_KEY", "some message", "error")
    r = repr(issue)
    assert "MY_KEY" in r
    assert "error" in r
    assert "some message" in r


def test_validation_result_empty_errors_and_warnings():
    result = ValidationResult()
    assert result.errors() == []
    assert result.warnings() == []
