"""Tests for envdiff.scoper."""

import pytest

from envdiff.scoper import ScopeResult, list_scopes, scope_env


@pytest.fixture
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET": "abc",
        "APP_NAME": "envdiff",
        "PLAIN": "no_prefix",
    }


def test_scope_env_returns_scope_result(sample_env):
    result = scope_env(sample_env, "DB")
    assert isinstance(result, ScopeResult)


def test_scope_env_filters_correct_keys(sample_env):
    result = scope_env(sample_env, "DB")
    assert set(result.stripped.keys()) == {"HOST", "PORT", "PASSWORD"}


def test_scope_env_strips_prefix_by_default(sample_env):
    result = scope_env(sample_env, "DB")
    assert "HOST" in result.stripped
    assert "DB_HOST" not in result.stripped


def test_scope_env_no_strip_prefix(sample_env):
    result = scope_env(sample_env, "DB", strip_prefix=False)
    assert "DB_HOST" in result.stripped
    assert "HOST" not in result.stripped


def test_scope_env_values_preserved(sample_env):
    result = scope_env(sample_env, "DB")
    assert result.stripped["HOST"] == "localhost"
    assert result.stripped["PORT"] == "5432"


def test_scope_env_empty_when_no_match(sample_env):
    result = scope_env(sample_env, "REDIS")
    assert len(result) == 0
    assert result.stripped == {}


def test_scope_env_case_insensitive_scope(sample_env):
    result_upper = scope_env(sample_env, "DB")
    result_lower = scope_env(sample_env, "db")
    assert result_upper.stripped == result_lower.stripped


def test_scope_env_scope_attribute_is_uppercase(sample_env):
    result = scope_env(sample_env, "aws")
    assert result.scope == "AWS"


def test_scope_result_len(sample_env):
    result = scope_env(sample_env, "AWS")
    assert len(result) == 2


def test_scope_result_restore(sample_env):
    result = scope_env(sample_env, "DB")
    restored = result.restore()
    assert restored["DB_HOST"] == "localhost"
    assert restored["DB_PORT"] == "5432"


def test_list_scopes_returns_sorted(sample_env):
    scopes = list_scopes(sample_env)
    assert scopes == sorted(scopes)


def test_list_scopes_finds_db_and_aws(sample_env):
    scopes = list_scopes(sample_env)
    assert "DB" in scopes
    assert "AWS" in scopes


def test_list_scopes_excludes_single_key_when_min_keys_2(sample_env):
    scopes = list_scopes(sample_env, min_keys=2)
    assert "APP" not in scopes
    assert "DB" in scopes


def test_list_scopes_excludes_plain_key(sample_env):
    scopes = list_scopes(sample_env)
    assert "PLAIN" not in scopes


def test_list_scopes_empty_env():
    assert list_scopes({}) == []
