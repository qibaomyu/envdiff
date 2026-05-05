"""Tests for envdiff.merger module."""

import pytest
from envdiff.merger import merge_envs, find_conflicts, MergeStrategy


@pytest.fixture
def env_a():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"}


@pytest.fixture
def env_b():
    return {"DB_HOST": "prod-db", "DB_PORT": "5432", "LOG_LEVEL": "warn"}


@pytest.fixture
def env_c():
    return {"DB_HOST": "staging-db", "CACHE_TTL": "300"}


def test_merge_union_includes_all_keys(env_a, env_b):
    result = merge_envs([env_a, env_b], strategy=MergeStrategy.UNION)
    assert "DB_HOST" in result
    assert "DEBUG" in result
    assert "LOG_LEVEL" in result


def test_merge_union_first_wins_on_conflict(env_a, env_b):
    result = merge_envs([env_a, env_b], strategy=MergeStrategy.UNION)
    assert result["DB_HOST"] == "localhost"  # env_a wins


def test_merge_first_wins(env_a, env_b):
    result = merge_envs([env_a, env_b], strategy=MergeStrategy.FIRST_WINS)
    assert result["DB_HOST"] == "localhost"
    assert result["LOG_LEVEL"] == "warn"


def test_merge_last_wins(env_a, env_b):
    result = merge_envs([env_a, env_b], strategy=MergeStrategy.LAST_WINS)
    assert result["DB_HOST"] == "prod-db"  # env_b overrides
    assert result["DEBUG"] == "true"


def test_merge_intersection_only_common_keys(env_a, env_b):
    result = merge_envs([env_a, env_b], strategy=MergeStrategy.INTERSECTION)
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_merge_intersection_values_from_first(env_a, env_b):
    result = merge_envs([env_a, env_b], strategy=MergeStrategy.INTERSECTION)
    assert result["DB_HOST"] == "localhost"


def test_merge_empty_list():
    assert merge_envs([]) == {}


def test_merge_single_env(env_a):
    result = merge_envs([env_a])
    assert result == env_a


def test_merge_unknown_strategy_raises(env_a, env_b):
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs([env_a, env_b], strategy="magic")


def test_find_conflicts_detects_differing_values(env_a, env_b):
    conflicts = find_conflicts([env_a, env_b], labels=["a", "b"])
    assert "DB_HOST" in conflicts
    assert conflicts["DB_HOST"] == {"a": "localhost", "b": "prod-db"}


def test_find_conflicts_no_conflict_for_same_value(env_a, env_b):
    conflicts = find_conflicts([env_a, env_b], labels=["a", "b"])
    assert "DB_PORT" not in conflicts


def test_find_conflicts_missing_key_not_included_as_conflict(env_a, env_b):
    # DEBUG only in env_a, so no "conflict" — only one source has it
    conflicts = find_conflicts([env_a, env_b], labels=["a", "b"])
    assert "DEBUG" not in conflicts


def test_find_conflicts_three_envs(env_a, env_b, env_c):
    conflicts = find_conflicts([env_a, env_b, env_c], labels=["a", "b", "c"])
    assert "DB_HOST" in conflicts
    assert conflicts["DB_HOST"]["c"] == "staging-db"


def test_find_conflicts_empty_envs():
    assert find_conflicts([]) == {}


def test_find_conflicts_auto_labels(env_a, env_b):
    conflicts = find_conflicts([env_a, env_b])
    assert "DB_HOST" in conflicts
    assert "0" in conflicts["DB_HOST"]
    assert "1" in conflicts["DB_HOST"]
