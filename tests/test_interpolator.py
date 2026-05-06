"""Tests for envdiff.interpolator."""

import pytest

from envdiff.interpolator import (
    InterpolationError,
    find_references,
    interpolate_env,
    interpolate_value,
)


# ---------------------------------------------------------------------------
# find_references
# ---------------------------------------------------------------------------

def test_find_references_single():
    assert find_references("${HOME}/bin") == ["HOME"]


def test_find_references_multiple():
    assert find_references("${HOST}:${PORT}") == ["HOST", "PORT"]


def test_find_references_none():
    assert find_references("no references here") == []


def test_find_references_empty_string():
    assert find_references("") == []


# ---------------------------------------------------------------------------
# interpolate_value
# ---------------------------------------------------------------------------

def test_interpolate_value_simple():
    env = {"NAME": "world"}
    assert interpolate_value("hello ${NAME}", env) == "hello world"


def test_interpolate_value_multiple_refs():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = interpolate_value("${HOST}:${PORT}", env)
    assert result == "localhost:5432"


def test_interpolate_value_missing_non_strict():
    result = interpolate_value("${MISSING}", {})
    assert result == "${MISSING}"


def test_interpolate_value_missing_strict():
    with pytest.raises(InterpolationError, match="MISSING"):
        interpolate_value("${MISSING}", {}, strict=True)


def test_interpolate_value_nested():
    env = {"BASE": "/opt", "DIR": "${BASE}/app"}
    assert interpolate_value("${DIR}/bin", env) == "/opt/app/bin"


def test_interpolate_value_circular_raises():
    env = {"A": "${B}", "B": "${A}"}
    with pytest.raises(InterpolationError, match="Circular"):
        interpolate_value("${A}", env)


def test_interpolate_value_no_references():
    assert interpolate_value("plain value", {}) == "plain value"


# ---------------------------------------------------------------------------
# interpolate_env
# ---------------------------------------------------------------------------

def test_interpolate_env_resolves_all():
    env = {"BASE_URL": "https://example.com", "API": "${BASE_URL}/api"}
    result = interpolate_env(env)
    assert result["API"] == "https://example.com/api"
    assert result["BASE_URL"] == "https://example.com"


def test_interpolate_env_leaves_original_unchanged():
    env = {"A": "hello", "B": "${A} world"}
    result = interpolate_env(env)
    assert env["B"] == "${A} world"  # original not mutated
    assert result["B"] == "hello world"


def test_interpolate_env_strict_raises_on_missing():
    env = {"KEY": "${UNDEFINED}"}
    with pytest.raises(InterpolationError):
        interpolate_env(env, strict=True)


def test_interpolate_env_empty():
    assert interpolate_env({}) == {}
