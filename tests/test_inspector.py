"""Tests for envdiff.inspector."""
import pytest
from envdiff.inspector import inspect_env, InspectEntry, InspectResult


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DEBUG": "true",
        "BASE_URL": "https://example.com",
        "CONFIG_PATH": "/etc/app/config.yaml",
        "EMPTY_VAR": "",
        "SPACED_VAR": "hello world",
        "SPECIAL_VAR": "p@$$w0rd!",
    }


def test_inspect_returns_inspect_result(sample_env):
    result = inspect_env(sample_env)
    assert isinstance(result, InspectResult)


def test_inspect_entry_count(sample_env):
    result = inspect_env(sample_env)
    assert len(result.entries) == len(sample_env)


def test_by_key_returns_entry(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("DB_HOST")
    assert entry is not None
    assert entry.key == "DB_HOST"


def test_by_key_missing_returns_none(sample_env):
    result = inspect_env(sample_env)
    assert result.by_key("NONEXISTENT") is None


def test_empty_value_detected(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("EMPTY_VAR")
    assert entry.is_empty is True


def test_non_empty_value_not_flagged(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("DB_HOST")
    assert entry.is_empty is False


def test_numeric_value_detected(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("DB_PORT")
    assert entry.is_numeric is True


def test_non_numeric_not_flagged(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("DB_HOST")
    assert entry.is_numeric is False


def test_boolean_value_detected(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("DEBUG")
    assert entry.is_boolean is True


def test_url_detected(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("BASE_URL")
    assert entry.is_url is True


def test_non_url_not_flagged(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("DB_HOST")
    assert entry.is_url is False


def test_path_detected(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("CONFIG_PATH")
    assert entry.is_path is True


def test_whitespace_detected(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("SPACED_VAR")
    assert entry.has_whitespace is True


def test_no_whitespace_flag_for_plain_value(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("DB_HOST")
    assert entry.has_whitespace is False


def test_special_chars_detected(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("SPECIAL_VAR")
    assert entry.has_special_chars is True


def test_summary_total(sample_env):
    result = inspect_env(sample_env)
    s = result.summary()
    assert s["total"] == len(sample_env)


def test_summary_empty_count(sample_env):
    result = inspect_env(sample_env)
    s = result.summary()
    assert s["empty"] == 1


def test_summary_url_count(sample_env):
    result = inspect_env(sample_env)
    s = result.summary()
    assert s["url"] == 1


def test_empty_env_produces_empty_result():
    result = inspect_env({})
    assert result.entries == []
    assert result.summary()["total"] == 0


def test_value_length_recorded(sample_env):
    result = inspect_env(sample_env)
    entry = result.by_key("DB_HOST")
    assert entry.length == len("localhost")
