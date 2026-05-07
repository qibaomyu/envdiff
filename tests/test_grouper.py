"""Tests for envdiff.grouper."""

import pytest
from envdiff.grouper import EnvGroup, group_by_prefix, group_by_regex


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_ACCESS_KEY": "AKIA…",
        "AWS_SECRET_KEY": "secret",
        "PORT": "8080",
        "DEBUG": "true",
    }


def test_group_by_prefix_creates_db_group(sample_env):
    groups = group_by_prefix(sample_env)
    assert "DB" in groups
    assert set(groups["DB"].keys) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_group_by_prefix_creates_aws_group(sample_env):
    groups = group_by_prefix(sample_env)
    assert "AWS" in groups
    assert set(groups["AWS"].keys) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}


def test_group_by_prefix_ungrouped_keys(sample_env):
    groups = group_by_prefix(sample_env)
    assert "__ungrouped__" in groups
    assert "PORT" in groups["__ungrouped__"].keys
    assert "DEBUG" in groups["__ungrouped__"].keys


def test_group_by_prefix_min_group_size_merges_small(sample_env):
    # AWS has 2 keys; DB has 3.  With min_group_size=3 AWS should be ungrouped.
    groups = group_by_prefix(sample_env, min_group_size=3)
    assert "AWS" not in groups
    ungrouped_keys = groups["__ungrouped__"].keys
    assert "AWS_ACCESS_KEY" in ungrouped_keys
    assert "AWS_SECRET_KEY" in ungrouped_keys


def test_group_by_prefix_keys_are_sorted(sample_env):
    groups = group_by_prefix(sample_env)
    assert groups["DB"].keys == sorted(groups["DB"].keys)


def test_group_by_prefix_empty_env():
    groups = group_by_prefix({})
    assert groups == {}


def test_env_group_len():
    g = EnvGroup(name="X", keys=["X_A", "X_B"])
    assert len(g) == 2


def test_group_by_regex_matches_pattern(sample_env):
    patterns = {"database": r"^DB_", "cloud": r"^AWS_"}
    groups = group_by_regex(sample_env, patterns)
    assert "database" in groups
    assert set(groups["database"].keys) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_group_by_regex_fallback_group(sample_env):
    patterns = {"database": r"^DB_"}
    groups = group_by_regex(sample_env, patterns, fallback_group="misc")
    assert "misc" in groups
    assert "PORT" in groups["misc"].keys


def test_group_by_regex_first_match_wins():
    env = {"DB_HOST": "localhost"}
    patterns = {"first": r"^DB", "second": r"DB_HOST"}
    groups = group_by_regex(env, patterns)
    assert "first" in groups
    assert "second" not in groups


def test_group_by_regex_empty_patterns(sample_env):
    groups = group_by_regex(sample_env, {})
    # all keys fall into fallback
    assert "__other__" in groups
    assert len(groups["__other__"].keys) == len(sample_env)
