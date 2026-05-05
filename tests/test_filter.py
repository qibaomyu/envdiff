"""Tests for envdiff.filter."""

import pytest

from envdiff.filter import filter_keys, filter_keys_by_prefix, filter_keys_by_regex


@pytest.fixture()
def sample_env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_HOST": "db.local",
        "DB_PASSWORD": "secret",
        "LOG_LEVEL": "INFO",
        "SECRET_KEY": "abc123",
    }


def test_filter_keys_include(sample_env):
    result = filter_keys(sample_env, include_patterns=["APP_*"])
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_keys_exclude(sample_env):
    result = filter_keys(sample_env, exclude_patterns=["*PASSWORD", "SECRET_*"])
    assert "DB_PASSWORD" not in result
    assert "SECRET_KEY" not in result
    assert "APP_HOST" in result


def test_filter_keys_include_and_exclude(sample_env):
    result = filter_keys(
        sample_env,
        include_patterns=["DB_*"],
        exclude_patterns=["*PASSWORD"],
    )
    assert set(result.keys()) == {"DB_HOST"}


def test_filter_keys_no_patterns_returns_all(sample_env):
    result = filter_keys(sample_env)
    assert result == sample_env


def test_filter_keys_include_no_match(sample_env):
    result = filter_keys(sample_env, include_patterns=["NONEXISTENT_*"])
    assert result == {}


def test_filter_keys_by_prefix(sample_env):
    result = filter_keys_by_prefix(sample_env, "DB_")
    assert set(result.keys()) == {"DB_HOST", "DB_PASSWORD"}


def test_filter_keys_by_prefix_no_match(sample_env):
    assert filter_keys_by_prefix(sample_env, "MISSING_") == {}


def test_filter_keys_by_regex_include(sample_env):
    result = filter_keys_by_regex(sample_env, r"^(APP|DB)_")
    assert set(result.keys()) == {"APP_HOST", "APP_PORT", "DB_HOST", "DB_PASSWORD"}


def test_filter_keys_by_regex_exclude(sample_env):
    result = filter_keys_by_regex(sample_env, r"PASSWORD|SECRET", exclude=True)
    assert "DB_PASSWORD" not in result
    assert "SECRET_KEY" not in result
    assert len(result) == 4


def test_filter_does_not_mutate_original(sample_env):
    original_keys = set(sample_env.keys())
    filter_keys(sample_env, include_patterns=["APP_*"], exclude_patterns=["*PORT"])
    assert set(sample_env.keys()) == original_keys
