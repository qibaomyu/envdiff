"""Tests for envdiff.transformer."""

import pytest

from envdiff.transformer import (
    TransformEntry,
    TransformResult,
    BUILT_IN_RULES,
    transform_env,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "  localhost  ",
        "DB_PASSWORD": "'secret123'",
        "APP_ENV": "production",
        "DEBUG": "FALSE",
    }


def test_built_in_rules_present():
    assert "uppercase" in BUILT_IN_RULES
    assert "lowercase" in BUILT_IN_RULES
    assert "strip" in BUILT_IN_RULES
    assert "strip_quotes" in BUILT_IN_RULES


def test_transform_strip_removes_whitespace(sample_env):
    result = transform_env(sample_env, rules=["strip"])
    assert result.env["DB_HOST"] == "localhost"


def test_transform_uppercase(sample_env):
    result = transform_env(sample_env, rules=["uppercase"])
    assert result.env["APP_ENV"] == "PRODUCTION"
    assert result.env["DEBUG"] == "FALSE"


def test_transform_lowercase(sample_env):
    result = transform_env(sample_env, rules=["lowercase"])
    assert result.env["APP_ENV"] == "production"
    assert result.env["DEBUG"] == "false"


def test_transform_strip_quotes(sample_env):
    result = transform_env(sample_env, rules=["strip_quotes"])
    assert result.env["DB_PASSWORD"] == "secret123"


def test_transform_chained_rules(sample_env):
    result = transform_env(sample_env, rules=["strip", "uppercase"])
    assert result.env["DB_HOST"] == "LOCALHOST"


def test_transform_keys_filter(sample_env):
    result = transform_env(sample_env, rules=["lowercase"], keys=["APP_ENV"])
    assert result.env["APP_ENV"] == "production"
    # Other keys should be unchanged
    assert result.env["DEBUG"] == "FALSE"


def test_transform_all_keys_when_no_filter(sample_env):
    result = transform_env(sample_env, rules=["lowercase"])
    assert result.env["DEBUG"] == "false"
    assert result.env["APP_ENV"] == "production"


def test_transform_result_changed_entries(sample_env):
    result = transform_env(sample_env, rules=["lowercase"])
    changed_keys = {e.key for e in result.changed()}
    assert "DEBUG" in changed_keys  # FALSE -> false
    assert "APP_ENV" not in changed_keys  # already lowercase


def test_transform_result_unchanged_entries(sample_env):
    result = transform_env(sample_env, rules=["lowercase"])
    unchanged_keys = {e.key for e in result.unchanged()}
    assert "APP_ENV" in unchanged_keys


def test_transform_summary_format(sample_env):
    result = transform_env(sample_env, rules=["uppercase"])
    s = result.summary()
    assert "/" in s
    assert "transformed" in s


def test_transform_unknown_rule_raises(sample_env):
    with pytest.raises(ValueError, match="Unknown transform rules"):
        transform_env(sample_env, rules=["nonexistent_rule"])


def test_transform_custom_rule(sample_env):
    def reverse(v: str) -> str:
        return v[::-1]

    result = transform_env(sample_env, rules=["reverse"], custom_rules={"reverse": reverse})
    assert result.env["APP_ENV"] == "noitcudorp"


def test_transform_empty_rules_no_change(sample_env):
    result = transform_env(sample_env, rules=[])
    for entry in result.entries:
        if entry.rule_applied != "skipped":
            assert entry.original == entry.transformed


def test_transform_entry_repr():
    e = TransformEntry("KEY", "old", "new", "uppercase")
    r = repr(e)
    assert "KEY" in r
    assert "uppercase" in r
