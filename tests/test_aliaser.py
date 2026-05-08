"""Tests for envdiff.aliaser."""
import pytest
from envdiff.aliaser import alias_env, AliasEntry, AliasResult


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "secret",
        "APP_ENV": "production",
        "LOG_LEVEL": "info",
    }


@pytest.fixture
def aliases():
    return {
        "DB_HOST": "database_host",
        "DB_PORT": "database_port",
        "DB_PASSWORD": "database_password",
    }


def test_alias_env_creates_entries(sample_env, aliases):
    result = alias_env(sample_env, aliases)
    assert len(result.entries) == 3


def test_alias_entry_original_key(sample_env, aliases):
    result = alias_env(sample_env, aliases)
    originals = {e.original_key for e in result.entries}
    assert "DB_HOST" in originals
    assert "DB_PORT" in originals


def test_alias_entry_alias_name(sample_env, aliases):
    result = alias_env(sample_env, aliases)
    by_alias = result.by_alias()
    assert "database_host" in by_alias
    assert by_alias["database_host"] == "localhost"


def test_alias_entry_value_preserved(sample_env, aliases):
    result = alias_env(sample_env, aliases)
    by_alias = result.by_alias()
    assert by_alias["database_port"] == "5432"


def test_unaliased_keys_included_by_default(sample_env, aliases):
    result = alias_env(sample_env, aliases)
    assert "APP_ENV" in result.unaliased
    assert "LOG_LEVEL" in result.unaliased


def test_unaliased_keys_excluded_when_flag_false(sample_env, aliases):
    result = alias_env(sample_env, aliases, include_unaliased=False)
    assert result.unaliased == {}


def test_aliased_keys_not_in_unaliased(sample_env, aliases):
    result = alias_env(sample_env, aliases)
    assert "DB_HOST" not in result.unaliased
    assert "DB_PASSWORD" not in result.unaliased


def test_missing_key_recorded(sample_env):
    result = alias_env(sample_env, {"NONEXISTENT_KEY": "my_alias"})
    assert "NONEXISTENT_KEY" in result.missing_keys


def test_missing_key_not_in_entries(sample_env):
    result = alias_env(sample_env, {"NONEXISTENT_KEY": "my_alias"})
    assert len(result.entries) == 0


def test_by_original_returns_correct_mapping(sample_env, aliases):
    result = alias_env(sample_env, aliases)
    by_orig = result.by_original()
    assert by_orig["DB_HOST"] == "localhost"


def test_empty_aliases_returns_all_unaliased(sample_env):
    result = alias_env(sample_env, {})
    assert result.entries == []
    assert result.unaliased == sample_env


def test_empty_env_no_entries():
    result = alias_env({}, {"DB_HOST": "host"})
    assert result.entries == []
    assert "DB_HOST" in result.missing_keys


def test_summary_contains_counts(sample_env, aliases):
    result = alias_env(sample_env, aliases)
    s = result.summary()
    assert "Aliased: 3" in s
    assert "Unaliased: 2" in s


def test_summary_lists_missing_keys(sample_env):
    result = alias_env(sample_env, {"GHOST": "ghost_alias"})
    s = result.summary()
    assert "GHOST" in s
