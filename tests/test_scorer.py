"""Tests for envdiff.scorer."""

import pytest

from envdiff.scorer import ScoreBreakdown, score_env


@pytest.fixture
def clean_env():
    return {
        "APP_NAME": "myapp",
        "PORT": "8080",
        "DEBUG": "false",
    }


@pytest.fixture
def dirty_env():
    return {
        "APP_NAME": "",
        "DB_PASSWORD": "supersecret",
        "API_KEY": "changeme",
        "PORT": "todo_fix",
    }


def test_clean_env_high_score(clean_env):
    result = score_env(clean_env)
    assert result.score() == 100.0


def test_clean_env_grade_a(clean_env):
    result = score_env(clean_env)
    assert result.grade() == "A"


def test_empty_value_penalised(dirty_env):
    result = score_env(dirty_env)
    assert result.empty_values == 1


def test_sensitive_unredacted_penalised(dirty_env):
    result = score_env(dirty_env)
    assert result.sensitive_unredacted >= 1


def test_suspicious_value_penalised(dirty_env):
    result = score_env(dirty_env)
    assert result.suspicious_keys >= 1


def test_dirty_env_lower_score(clean_env, dirty_env):
    clean_score = score_env(clean_env).score()
    dirty_score = score_env(dirty_env).score()
    assert dirty_score < clean_score


def test_penalties_list_populated(dirty_env):
    result = score_env(dirty_env)
    assert len(result.penalties) > 0


def test_empty_env_returns_perfect_score():
    result = score_env({})
    assert result.score() == 100.0
    assert result.grade() == "A"


def test_score_breakdown_total_keys(clean_env):
    result = score_env(clean_env)
    assert result.total_keys == 3


def test_grade_f_for_very_bad_env():
    env = {
        "SECRET_KEY": "changeme",
        "DB_PASSWORD": "placeholder",
        "API_TOKEN": "fixme",
        "EMPTY_KEY": "",
    }
    result = score_env(env)
    assert result.grade() in ("D", "F")


def test_redacted_value_not_penalised():
    env = {"DB_PASSWORD": "[REDACTED]"}
    result = score_env(env)
    assert result.sensitive_unredacted == 0
