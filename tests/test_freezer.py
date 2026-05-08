"""Tests for envdiff.freezer."""

import json
import os
import pytest

from envdiff.freezer import (
    FreezeViolation,
    FreezeResult,
    freeze_env,
    load_freeze,
    check_freeze,
    FREEZE_VERSION,
)


@pytest.fixture()
def freeze_file(tmp_path):
    return str(tmp_path / "env.freeze.json")


@pytest.fixture()
def sample_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production"}


# --- freeze_env ---

def test_freeze_creates_file(freeze_file, sample_env):
    freeze_env(sample_env, freeze_file)
    assert os.path.exists(freeze_file)


def test_freeze_file_contains_version(freeze_file, sample_env):
    freeze_env(sample_env, freeze_file)
    with open(freeze_file) as fh:
        data = json.load(fh)
    assert data["version"] == FREEZE_VERSION


def test_freeze_file_contains_env(freeze_file, sample_env):
    freeze_env(sample_env, freeze_file)
    with open(freeze_file) as fh:
        data = json.load(fh)
    assert data["env"] == sample_env


def test_freeze_file_stores_label(freeze_file, sample_env):
    freeze_env(sample_env, freeze_file, label="prod-baseline")
    with open(freeze_file) as fh:
        data = json.load(fh)
    assert data["label"] == "prod-baseline"


# --- load_freeze ---

def test_load_freeze_roundtrip(freeze_file, sample_env):
    freeze_env(sample_env, freeze_file)
    loaded = load_freeze(freeze_file)
    assert loaded == sample_env


def test_load_freeze_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_freeze(str(tmp_path / "nonexistent.json"))


def test_load_freeze_bad_version(freeze_file):
    with open(freeze_file, "w") as fh:
        json.dump({"version": "99", "env": {}}, fh)
    with pytest.raises(ValueError, match="Unsupported freeze file version"):
        load_freeze(freeze_file)


# --- check_freeze ---

def test_check_freeze_no_violations(sample_env):
    result = check_freeze(frozen=sample_env, actual=sample_env.copy())
    assert not result.has_violations()
    assert result.frozen_keys == list(sample_env.keys())


def test_check_freeze_detects_changed_value(sample_env):
    actual = {**sample_env, "DB_HOST": "remotehost"}
    result = check_freeze(frozen=sample_env, actual=actual)
    assert result.has_violations()
    assert any(v.key == "DB_HOST" for v in result.violations)


def test_check_freeze_detects_missing_key(sample_env):
    actual = {k: v for k, v in sample_env.items() if k != "APP_ENV"}
    result = check_freeze(frozen=sample_env, actual=actual)
    assert any(v.key == "APP_ENV" and v.actual is None for v in result.violations)


def test_check_freeze_summary_ok(sample_env):
    result = check_freeze(frozen=sample_env, actual=sample_env.copy())
    assert "OK" in result.summary()


def test_check_freeze_summary_lists_violations(sample_env):
    actual = {**sample_env, "DB_PORT": "9999"}
    result = check_freeze(frozen=sample_env, actual=actual)
    summary = result.summary()
    assert "DB_PORT" in summary
    assert "9999" in summary
