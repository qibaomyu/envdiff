"""Tests for envdiff.comparator module."""

import pytest
from envdiff.comparator import compare_envs, EnvDiffResult


ENV_STAGING = {
    "DB_HOST": "staging-db.internal",
    "DB_PORT": "5432",
    "DEBUG": "true",
    "LOG_LEVEL": "debug",
}

ENV_PROD = {
    "DB_HOST": "prod-db.internal",
    "DB_PORT": "5432",
    "DEBUG": "false",
    "SENTRY_DSN": "https://sentry.io/xyz",
}


def test_compare_only_in_a():
    result = compare_envs(ENV_STAGING, ENV_PROD, "staging", "prod")
    assert "LOG_LEVEL" in result.only_in_a
    assert "SENTRY_DSN" not in result.only_in_a


def test_compare_only_in_b():
    result = compare_envs(ENV_STAGING, ENV_PROD, "staging", "prod")
    assert "SENTRY_DSN" in result.only_in_b
    assert "LOG_LEVEL" not in result.only_in_b


def test_compare_value_differs():
    result = compare_envs(ENV_STAGING, ENV_PROD, "staging", "prod")
    assert "DB_HOST" in result.value_differs
    assert result.value_differs["DB_HOST"] == ("staging-db.internal", "prod-db.internal")
    assert "DEBUG" in result.value_differs
    assert result.value_differs["DEBUG"] == ("true", "false")


def test_compare_common_keys():
    result = compare_envs(ENV_STAGING, ENV_PROD, "staging", "prod")
    assert "DB_PORT" in result.common_keys


def test_compare_has_differences():
    result = compare_envs(ENV_STAGING, ENV_PROD)
    assert result.has_differences is True


def test_compare_no_differences():
    env = {"KEY": "value"}
    result = compare_envs(env, env, "a", "b")
    assert result.has_differences is False
    assert "KEY" in result.common_keys


def test_compare_ignore_keys():
    result = compare_envs(
        ENV_STAGING, ENV_PROD, "staging", "prod", ignore_keys=["DEBUG", "LOG_LEVEL"]
    )
    assert "DEBUG" not in result.value_differs
    assert "LOG_LEVEL" not in result.only_in_a


def test_summary_output():
    result = compare_envs(ENV_STAGING, ENV_PROD, "staging", "prod")
    summary = result.summary
    assert "staging" in summary
    assert "prod" in summary
    assert "Value differences" in summary
