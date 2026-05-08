"""Tests for envdiff.differ_summary."""
from __future__ import annotations

import pytest

from envdiff.differ import diff_envs
from envdiff.differ_summary import DiffSummary, summarize_diff, text_diff_summary


@pytest.fixture()
def before_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "old-key",
        "SHARED": "same",
    }


@pytest.fixture()
def after_env() -> dict:
    return {
        "DB_HOST": "prod.db",   # modified
        "DB_PORT": "5432",      # unchanged
        "NEW_KEY": "hello",     # added
        "SHARED": "same",       # unchanged
        # API_KEY removed
    }


@pytest.fixture()
def summary(before_env, after_env) -> DiffSummary:
    changelog = diff_envs(before_env, after_env)
    return summarize_diff(changelog)


def test_summary_added_count(summary):
    assert summary.added == 1


def test_summary_removed_count(summary):
    assert summary.removed == 1


def test_summary_modified_count(summary):
    assert summary.modified == 1


def test_summary_unchanged_count(summary):
    assert summary.unchanged == 2


def test_summary_total_count(summary):
    assert summary.total == 5


def test_by_type_added_key(summary):
    keys = [e.key for e in summary.by_type["added"]]
    assert "NEW_KEY" in keys


def test_by_type_removed_key(summary):
    keys = [e.key for e in summary.by_type["removed"]]
    assert "API_KEY" in keys


def test_by_type_modified_key(summary):
    keys = [e.key for e in summary.by_type["modified"]]
    assert "DB_HOST" in keys


def test_text_summary_contains_total(summary):
    text = text_diff_summary(summary)
    assert "Total keys" in text
    assert str(summary.total) in text


def test_text_summary_contains_added(summary):
    text = text_diff_summary(summary)
    assert "Added" in text


def test_text_summary_contains_removed(summary):
    text = text_diff_summary(summary)
    assert "Removed" in text


def test_identical_envs_no_changes():
    env = {"A": "1", "B": "2"}
    changelog = diff_envs(env, env)
    s = summarize_diff(changelog)
    assert s.added == 0
    assert s.removed == 0
    assert s.modified == 0
    assert s.unchanged == 2
