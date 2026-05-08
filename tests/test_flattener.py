"""Tests for envdiff.flattener."""
import json
import pytest

from envdiff.flattener import (
    FlattenEntry,
    FlattenResult,
    flatten_env,
    _flatten_dict,
)


@pytest.fixture
def sample_env():
    return {
        "PLAIN": "hello",
        "DB_CONFIG": json.dumps({"host": "localhost", "port": "5432"}),
        "NESTED": json.dumps({"a": {"b": "deep"}}),
        "NOT_JSON": "just-a-string",
    }


# ---------------------------------------------------------------------------
# _flatten_dict
# ---------------------------------------------------------------------------

def test_flatten_dict_simple():
    result = _flatten_dict({"host": "localhost", "port": "5432"}, prefix="DB")
    assert result == {"DB.host": "localhost", "DB.port": "5432"}


def test_flatten_dict_nested():
    result = _flatten_dict({"a": {"b": "deep"}}, prefix="ROOT")
    assert result == {"ROOT.a.b": "deep"}


def test_flatten_dict_custom_separator():
    result = _flatten_dict({"x": "1"}, prefix="P", separator="__")
    assert "P__x" in result


# ---------------------------------------------------------------------------
# flatten_env
# ---------------------------------------------------------------------------

def test_flatten_env_returns_flatten_result(sample_env):
    result = flatten_env(sample_env)
    assert isinstance(result, FlattenResult)


def test_flatten_env_expands_json_object(sample_env):
    env = flatten_env(sample_env).as_env()
    assert "DB_CONFIG.host" in env
    assert "DB_CONFIG.port" in env
    assert env["DB_CONFIG.host"] == "localhost"


def test_flatten_env_expands_nested_json(sample_env):
    env = flatten_env(sample_env).as_env()
    assert "NESTED.a.b" in env
    assert env["NESTED.a.b"] == "deep"


def test_flatten_env_plain_value_unchanged(sample_env):
    env = flatten_env(sample_env).as_env()
    assert env.get("PLAIN") == "hello"


def test_flatten_env_non_json_kept(sample_env):
    env = flatten_env(sample_env).as_env()
    assert env.get("NOT_JSON") == "just-a-string"


def test_flatten_env_original_json_key_not_present(sample_env):
    env = flatten_env(sample_env).as_env()
    # The original DB_CONFIG key should be replaced by its expanded children
    assert "DB_CONFIG" not in env


def test_flatten_env_skipped_lists_plain_keys(sample_env):
    result = flatten_env(sample_env)
    assert "PLAIN" in result.skipped
    assert "NOT_JSON" in result.skipped


def test_flatten_env_summary_string(sample_env):
    result = flatten_env(sample_env)
    s = result.summary()
    assert "Flattened" in s
    assert "skipped" in s


def test_flatten_env_empty_env():
    result = flatten_env({})
    assert result.as_env() == {}
    assert result.skipped == []


def test_flatten_entry_repr():
    entry = FlattenEntry("DB", "DB.host", "localhost")
    assert "DB" in repr(entry)
    assert "DB.host" in repr(entry)


def test_flatten_env_custom_separator():
    env = {"CFG": json.dumps({"key": "val"})}
    result = flatten_env(env, separator="__")
    assert "CFG__key" in result.as_env()


def test_flatten_env_json_list_not_expanded():
    """A JSON array value should not be expanded (not a dict)."""
    env = {"ITEMS": json.dumps(["a", "b"])}
    result = flatten_env(env)
    assert result.as_env().get("ITEMS") == json.dumps(["a", "b"])
