"""Edge-case tests for envdiff.differ_summary."""
from __future__ import annotations

from envdiff.differ import diff_envs
from envdiff.differ_summary import summarize_diff, text_diff_summary


def test_empty_before_all_added():
    changelog = diff_envs({}, {"A": "1", "B": "2"})
    s = summarize_diff(changelog)
    assert s.added == 2
    assert s.removed == 0
    assert s.unchanged == 0


def test_empty_after_all_removed():
    changelog = diff_envs({"A": "1", "B": "2"}, {})
    s = summarize_diff(changelog)
    assert s.removed == 2
    assert s.added == 0
    assert s.unchanged == 0


def test_both_empty_zero_total():
    changelog = diff_envs({}, {})
    s = summarize_diff(changelog)
    assert s.total == 0
    assert s.added == 0
    assert s.removed == 0
    assert s.modified == 0
    assert s.unchanged == 0


def test_text_summary_all_zeros():
    changelog = diff_envs({}, {})
    s = summarize_diff(changelog)
    text = text_diff_summary(s)
    assert "0" in text


def test_by_type_keys_always_present():
    changelog = diff_envs({}, {})
    s = summarize_diff(changelog)
    for key in ("added", "removed", "modified", "unchanged"):
        assert key in s.by_type


def test_total_equals_sum_of_parts():
    before = {"A": "1", "B": "2", "C": "3"}
    after = {"A": "changed", "C": "3", "D": "new"}
    changelog = diff_envs(before, after)
    s = summarize_diff(changelog)
    assert s.total == s.added + s.removed + s.modified + s.unchanged


def test_repr_contains_counts():
    before = {"X": "1"}
    after = {"X": "2"}
    changelog = diff_envs(before, after)
    s = summarize_diff(changelog)
    r = repr(s)
    assert "modified=1" in r
