"""Tests for envdiff.masker."""

import pytest

from envdiff.masker import (
    DEFAULT_MASK,
    MaskResult,
    mask_env,
    mask_summary,
    mask_value,
)


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abc123xyz",
        "APP_NAME": "envdiff",
        "PORT": "8080",
    }


# --- mask_value ---

def test_mask_value_returns_default_mask():
    assert mask_value("mysecret") == DEFAULT_MASK


def test_mask_value_custom_mask():
    assert mask_value("mysecret", mask="[hidden]") == "[hidden]"


def test_mask_value_empty_string_unchanged():
    assert mask_value("") == ""


def test_mask_value_partial_reveals_suffix():
    result = mask_value("supersecret", partial=True)
    assert result.endswith("cret")
    assert result.startswith(DEFAULT_MASK)


def test_mask_value_partial_short_value_fully_masked():
    # value shorter than _PARTIAL_VISIBLE chars should be fully masked
    result = mask_value("ab", partial=True)
    assert result == DEFAULT_MASK


# --- mask_env ---

def test_mask_env_masks_specified_keys(sample_env):
    results = mask_env(sample_env, ["DB_PASSWORD", "API_KEY"])
    assert results["DB_PASSWORD"].was_masked is True
    assert results["API_KEY"].was_masked is True


def test_mask_env_does_not_mask_other_keys(sample_env):
    results = mask_env(sample_env, ["DB_PASSWORD"])
    assert results["APP_NAME"].was_masked is False
    assert results["APP_NAME"].masked_value == "envdiff"


def test_mask_env_all_keys_present_in_result(sample_env):
    results = mask_env(sample_env, [])
    assert set(results.keys()) == set(sample_env.keys())


def test_mask_env_masked_value_is_mask_string(sample_env):
    results = mask_env(sample_env, ["DB_PASSWORD"])
    assert results["DB_PASSWORD"].masked_value == DEFAULT_MASK


def test_mask_env_partial_mode(sample_env):
    results = mask_env(sample_env, ["API_KEY"], partial=True)
    assert results["API_KEY"].masked_value.endswith("xyz")


def test_mask_env_unknown_key_in_list(sample_env):
    # Keys not in env are simply ignored
    results = mask_env(sample_env, ["NONEXISTENT"])
    assert "NONEXISTENT" not in results


# --- mask_summary ---

def test_mask_summary_correct_count(sample_env):
    results = mask_env(sample_env, ["DB_PASSWORD", "API_KEY"])
    summary = mask_summary(results)
    assert summary == "2/4 keys masked."


def test_mask_summary_none_masked(sample_env):
    results = mask_env(sample_env, [])
    assert mask_summary(results) == "0/4 keys masked."
