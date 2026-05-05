"""Tests for envdiff.differ module."""
import pytest
from envdiff.differ import (
    diff_snapshots,
    format_changelog,
    ChangeEntry,
    DiffChangelog,
)


@pytest.fixture
def before_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}


@pytest.fixture
def after_env():
    return {"DB_HOST": "prod.db", "DB_PORT": "5432", "NEW_KEY": "hello"}


def test_diff_detects_added(before_env, after_env):
    changelog = diff_snapshots(before_env, after_env)
    keys = [e.key for e in changelog.added]
    assert "NEW_KEY" in keys


def test_diff_detects_removed(before_env, after_env):
    changelog = diff_snapshots(before_env, after_env)
    keys = [e.key for e in changelog.removed]
    assert "SECRET" in keys


def test_diff_detects_modified(before_env, after_env):
    changelog = diff_snapshots(before_env, after_env)
    keys = [e.key for e in changelog.modified]
    assert "DB_HOST" in keys


def test_diff_unchanged_not_included_by_default(before_env, after_env):
    changelog = diff_snapshots(before_env, after_env)
    assert changelog.unchanged == []


def test_diff_unchanged_included_when_flag_set(before_env, after_env):
    changelog = diff_snapshots(before_env, after_env, include_unchanged=True)
    keys = [e.key for e in changelog.unchanged]
    assert "DB_PORT" in keys


def test_diff_has_changes_true(before_env, after_env):
    changelog = diff_snapshots(before_env, after_env)
    assert changelog.has_changes is True


def test_diff_has_changes_false():
    env = {"A": "1", "B": "2"}
    changelog = diff_snapshots(env, env.copy())
    assert changelog.has_changes is False


def test_diff_identical_envs_all_entries_unchanged():
    env = {"X": "foo"}
    changelog = diff_snapshots(env, env.copy(), include_unchanged=True)
    assert len(changelog.unchanged) == 1
    assert changelog.unchanged[0].change_type == "unchanged"


def test_diff_modified_entry_values():
    changelog = diff_snapshots({"K": "old"}, {"K": "new"})
    assert changelog.modified[0].old_value == "old"
    assert changelog.modified[0].new_value == "new"


def test_format_changelog_contains_added(before_env, after_env):
    changelog = diff_snapshots(before_env, after_env)
    output = format_changelog(changelog)
    assert "+ NEW_KEY" in output


def test_format_changelog_contains_removed(before_env, after_env):
    changelog = diff_snapshots(before_env, after_env)
    output = format_changelog(changelog)
    assert "- SECRET" in output


def test_format_changelog_contains_modified(before_env, after_env):
    changelog = diff_snapshots(before_env, after_env)
    output = format_changelog(changelog)
    assert "~ DB_HOST" in output


def test_format_changelog_no_changes():
    changelog = DiffChangelog()
    output = format_changelog(changelog)
    assert "(no changes)" in output


def test_format_changelog_custom_labels():
    changelog = DiffChangelog()
    output = format_changelog(changelog, label_before="v1", label_after="v2")
    assert "v1 -> v2" in output
