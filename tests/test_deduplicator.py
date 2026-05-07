"""Tests for envdiff.deduplicator."""

import pytest

from envdiff.deduplicator import (
    DeduplicationResult,
    DuplicateGroup,
    find_duplicates,
)


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "CACHE_HOST": "localhost",
        "APP_SECRET": "s3cr3t",
        "BACKUP_SECRET": "s3cr3t",
        "LOG_LEVEL": "info",
        "EMPTY_A": "",
        "EMPTY_B": "",
    }


# --- find_duplicates ---

def test_find_duplicates_detects_shared_value(sample_env):
    result = find_duplicates(sample_env)
    values_found = {g.value for g in result.groups}
    assert "localhost" in values_found
    assert "s3cr3t" in values_found


def test_find_duplicates_ignores_empty_by_default(sample_env):
    result = find_duplicates(sample_env)
    values_found = {g.value for g in result.groups}
    assert "" not in values_found


def test_find_duplicates_includes_empty_when_flag_false(sample_env):
    result = find_duplicates(sample_env, ignore_empty=False)
    values_found = {g.value for g in result.groups}
    assert "" in values_found


def test_find_duplicates_unique_values_no_groups():
    env = {"A": "1", "B": "2", "C": "3"}
    result = find_duplicates(env)
    assert not result.has_duplicates
    assert result.groups == []


def test_find_duplicates_ignore_keys(sample_env):
    result = find_duplicates(sample_env, ignore_keys=["CACHE_HOST"])
    keys_in_groups = {k for g in result.groups for k in g.keys}
    assert "CACHE_HOST" not in keys_in_groups


def test_find_duplicates_ignore_keys_removes_whole_group():
    env = {"A": "same", "B": "same"}
    result = find_duplicates(env, ignore_keys=["A", "B"])
    assert not result.has_duplicates


# --- DeduplicationResult ---

def test_has_duplicates_true(sample_env):
    result = find_duplicates(sample_env)
    assert result.has_duplicates is True


def test_has_duplicates_false():
    result = find_duplicates({"X": "unique"})
    assert result.has_duplicates is False


def test_total_duplicate_keys(sample_env):
    result = find_duplicates(sample_env)
    # localhost -> 2 keys, s3cr3t -> 2 keys
    assert result.total_duplicate_keys == 4


def test_summary_no_duplicates():
    result = DeduplicationResult(groups=[])
    assert result.summary() == "No duplicate values found."


def test_summary_lists_groups(sample_env):
    result = find_duplicates(sample_env)
    summary = result.summary()
    assert "localhost" in summary
    assert "s3cr3t" in summary


def test_groups_sorted_deterministically():
    env = {"Z_KEY": "val", "A_KEY": "val", "M_KEY": "other", "B_KEY": "other"}
    result = find_duplicates(env)
    assert len(result.groups) == 2
    # first group should start with A_KEY (alphabetically first)
    assert sorted(result.groups[0].keys)[0] == "A_KEY"


# --- DuplicateGroup ---

def test_duplicate_group_len():
    g = DuplicateGroup(value="x", keys=["A", "B", "C"])
    assert len(g) == 3
