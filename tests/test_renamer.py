"""Tests for envdiff.renamer."""

import pytest
from envdiff.renamer import rename_keys, RenameEntry, RenameResult


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
    }


def test_basic_rename(sample_env):
    result = rename_keys(sample_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert "DB_HOST" not in result.env
    assert result.env["DATABASE_HOST"] == "localhost"


def test_rename_removes_old_key(sample_env):
    result = rename_keys(sample_env, {"DB_PORT": "DATABASE_PORT"})
    assert "DB_PORT" not in result.env


def test_keep_original_flag(sample_env):
    result = rename_keys(sample_env, {"DB_HOST": "DATABASE_HOST"}, keep_original=True)
    assert "DB_HOST" in result.env
    assert "DATABASE_HOST" in result.env


def test_missing_key_is_skipped(sample_env):
    result = rename_keys(sample_env, {"MISSING_KEY": "NEW_KEY"})
    skipped = result.skipped()
    assert len(skipped) == 1
    assert skipped[0].skip_reason == "key not found"


def test_target_exists_no_overwrite(sample_env):
    env = dict(sample_env)
    env["DATABASE_HOST"] = "remote"
    result = rename_keys(env, {"DB_HOST": "DATABASE_HOST"}, overwrite=False)
    skipped = result.skipped()
    assert len(skipped) == 1
    assert skipped[0].skip_reason == "target key exists"
    assert result.env["DATABASE_HOST"] == "remote"  # unchanged


def test_target_exists_with_overwrite(sample_env):
    env = dict(sample_env)
    env["DATABASE_HOST"] = "remote"
    result = rename_keys(env, {"DB_HOST": "DATABASE_HOST"}, overwrite=True)
    assert result.env["DATABASE_HOST"] == "localhost"
    assert len(result.skipped()) == 0


def test_multiple_renames(sample_env):
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = rename_keys(sample_env, mapping)
    assert "DATABASE_HOST" in result.env
    assert "DATABASE_PORT" in result.env
    assert "DB_HOST" not in result.env
    assert "DB_PORT" not in result.env
    assert len(result.renamed()) == 2


def test_summary_string(sample_env):
    mapping = {"DB_HOST": "DATABASE_HOST", "MISSING": "X"}
    result = rename_keys(sample_env, mapping)
    assert "1 key(s) renamed" in result.summary()
    assert "1 skipped" in result.summary()


def test_empty_mapping_returns_original(sample_env):
    result = rename_keys(sample_env, {})
    assert result.env == sample_env
    assert result.entries == []


def test_empty_env():
    result = rename_keys({}, {"A": "B"})
    assert result.env == {}
    assert result.skipped()[0].skip_reason == "key not found"
