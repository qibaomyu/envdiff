"""Tests for envdiff.normalizer."""

import pytest
from envdiff.normalizer import normalize_key, normalize_value, normalize_env


# ---------------------------------------------------------------------------
# normalize_key
# ---------------------------------------------------------------------------

def test_normalize_key_uppercase():
    assert normalize_key("db_host") == "DB_HOST"


def test_normalize_key_strips_whitespace():
    assert normalize_key("  APP_ENV  ") == "APP_ENV"


def test_normalize_key_no_uppercase():
    assert normalize_key("db_host", uppercase=False) == "db_host"


def test_normalize_key_no_strip():
    assert normalize_key("  key  ", strip=False) == "  KEY  "


# ---------------------------------------------------------------------------
# normalize_value
# ---------------------------------------------------------------------------

def test_normalize_value_strips_whitespace():
    assert normalize_value("  hello  ") == "hello"


def test_normalize_value_removes_double_quotes():
    assert normalize_value('"my value"') == "my value"


def test_normalize_value_removes_single_quotes():
    assert normalize_value("'my value'") == "my value"


def test_normalize_value_no_remove_quotes():
    assert normalize_value('"quoted"', remove_quotes=False) == '"quoted"'


def test_normalize_value_collapse_whitespace():
    assert normalize_value("hello   world", collapse_whitespace=True) == "hello world"


def test_normalize_value_short_quoted_string_unchanged():
    """A single-char value like '"' should not be stripped of quotes."""
    assert normalize_value('"') == '"'


def test_normalize_value_mismatched_quotes_unchanged():
    assert normalize_value('"value\'') == '"value\''


# ---------------------------------------------------------------------------
# normalize_env
# ---------------------------------------------------------------------------

def test_normalize_env_uppercases_keys():
    env = {"db_host": "localhost", "app_env": "production"}
    result = normalize_env(env)
    assert "DB_HOST" in result
    assert "APP_ENV" in result


def test_normalize_env_strips_values():
    env = {"KEY": "  value  "}
    result = normalize_env(env)
    assert result["KEY"] == "value"


def test_normalize_env_removes_quotes_from_values():
    env = {"SECRET": '"s3cr3t"'}
    result = normalize_env(env)
    assert result["SECRET"] == "s3cr3t"


def test_normalize_env_deduplicates_case_variants():
    """When uppercase_keys=True, 'foo' and 'FOO' collapse to one entry."""
    env = {"foo": "first", "FOO": "second"}
    result = normalize_env(env)
    assert len(result) == 1
    assert result["FOO"] == "second"


def test_normalize_env_preserves_all_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    result = normalize_env(env)
    assert set(result.keys()) == {"A", "B", "C"}


def test_normalize_env_empty_dict():
    assert normalize_env({}) == {}


def test_normalize_env_collapse_whitespace_in_values():
    env = {"MSG": "hello   world"}
    result = normalize_env(env, collapse_whitespace=True)
    assert result["MSG"] == "hello world"
