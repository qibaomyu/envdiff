"""Tests for envdiff.linter."""

import pytest
from envdiff.linter import lint_env, LintIssue, LintResult


@pytest.fixture
def clean_env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "APP_PORT": "8080",
        "DEBUG": "false",
    }


def test_clean_env_no_issues(clean_env):
    result = lint_env(clean_env)
    assert not result.has_issues()


def test_summary_no_issues(clean_env):
    result = lint_env(clean_env)
    assert result.summary() == "0 error(s), 0 warning(s)"


def test_lowercase_key_warning():
    result = lint_env({"myKey": "value"})
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_lowercase_key_allowed_when_flag_set():
    result = lint_env({"myKey": "value"}, allow_lowercase=True)
    codes = [i.code for i in result.issues]
    assert "W001" not in codes


def test_key_starting_with_digit_is_error():
    result = lint_env({"1BAD_KEY": "value"})
    errors = result.errors()
    assert any(i.code == "E001" for i in errors)


def test_double_underscore_warning():
    result = lint_env({"APP__NAME": "foo"})
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_empty_value_warning():
    result = lint_env({"EMPTY_KEY": ""})
    codes = [i.code for i in result.issues]
    assert "W004" in codes


def test_whitespace_in_value_warning():
    result = lint_env({"PADDED": "  value  "})
    codes = [i.code for i in result.issues]
    assert "W003" in codes


def test_unmatched_double_quote_warning():
    result = lint_env({"BAD_QUOTE": '"unmatched'})
    codes = [i.code for i in result.issues]
    assert "W005" in codes


def test_unmatched_single_quote_warning():
    result = lint_env({"BAD_QUOTE": "'unmatched"})
    codes = [i.code for i in result.issues]
    assert "W005" in codes


def test_matched_quotes_no_warning():
    result = lint_env({"QUOTED": '"hello"'})
    codes = [i.code for i in result.issues]
    assert "W005" not in codes


def test_errors_and_warnings_separated():
    result = lint_env({"1BAD": "", "good_lower": "val"})
    assert len(result.errors()) >= 1
    assert len(result.warnings()) >= 1


def test_lint_issue_repr():
    issue = LintIssue("MY_KEY", "W001", "some message")
    assert "W001" in repr(issue)
    assert "MY_KEY" in repr(issue)


def test_multiple_issues_same_key():
    # lowercase + empty value
    result = lint_env({"badKey": ""})
    keys = [i.key for i in result.issues]
    assert keys.count("badKey") >= 2
