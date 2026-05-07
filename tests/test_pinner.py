"""Tests for envdiff.pinner."""

import pytest

from envdiff.pinner import PinViolation, PinResult, pin_env


@pytest.fixture
def pinned():
    return {"DB_HOST": "localhost", "APP_ENV": "production", "PORT": "8080"}


@pytest.fixture
def matching_actual():
    return {"DB_HOST": "localhost", "APP_ENV": "production", "PORT": "8080", "EXTRA": "ok"}


def test_no_violations_when_all_match(pinned, matching_actual):
    result = pin_env(pinned, matching_actual)
    assert not result.has_violations()


def test_pinned_keys_recorded(pinned, matching_actual):
    result = pin_env(pinned, matching_actual)
    assert set(result.pinned_keys) == set(pinned.keys())


def test_changed_value_is_violation(pinned):
    actual = {"DB_HOST": "remotehost", "APP_ENV": "production", "PORT": "8080"}
    result = pin_env(pinned, actual)
    assert result.has_violations()
    v = result.violations[0]
    assert v.key == "DB_HOST"
    assert v.reason == "changed"
    assert v.pinned_value == "localhost"
    assert v.actual_value == "remotehost"


def test_missing_key_is_violation(pinned):
    actual = {"APP_ENV": "production", "PORT": "8080"}  # DB_HOST absent
    result = pin_env(pinned, actual)
    assert result.has_violations()
    missing = [v for v in result.violations if v.reason == "missing"]
    assert len(missing) == 1
    assert missing[0].key == "DB_HOST"
    assert missing[0].actual_value is None


def test_extra_key_allowed_by_default(pinned):
    actual = {**pinned, "SURPRISE": "value"}
    result = pin_env(pinned, actual, allow_extra=True)
    assert not result.has_violations()


def test_extra_key_violation_when_not_allowed(pinned):
    actual = {**pinned, "SURPRISE": "value"}
    result = pin_env(pinned, actual, allow_extra=False)
    unexpected = [v for v in result.violations if v.reason == "unexpected"]
    assert len(unexpected) == 1
    assert unexpected[0].key == "SURPRISE"


def test_multiple_violations(pinned):
    actual = {"DB_HOST": "changed", "PORT": "9090"}  # APP_ENV missing
    result = pin_env(pinned, actual)
    assert len(result.violations) == 3  # changed x2, missing x1
    reasons = {v.reason for v in result.violations}
    assert "changed" in reasons
    assert "missing" in reasons


def test_summary_no_violations(pinned, matching_actual):
    result = pin_env(pinned, matching_actual)
    assert "match" in result.summary()
    assert str(len(pinned)) in result.summary()


def test_summary_with_violations(pinned):
    actual = {"DB_HOST": "other", "APP_ENV": "production", "PORT": "8080"}
    result = pin_env(pinned, actual)
    summary = result.summary()
    assert "violation" in summary
    assert "CHANGED" in summary
    assert "DB_HOST" in summary


def test_empty_pinned_no_violations():
    result = pin_env({}, {"ANY": "value"})
    assert not result.has_violations()
    assert result.pinned_keys == []


def test_empty_actual_all_missing():
    pinned = {"KEY": "val"}
    result = pin_env(pinned, {})
    assert result.has_violations()
    assert result.violations[0].reason == "missing"
