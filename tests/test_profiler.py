"""Tests for envdiff.profiler."""

import pytest
from envdiff.profiler import profile_env, _categorize, EnvProfile, ProfileEntry


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "abc123",
        "LOG_LEVEL": "INFO",
        "FEATURE_FLAG_X": "true",
        "AWS_REGION": "us-east-1",
        "APP_NAME": "myapp",
        "EMPTY_VAR": "",
    }


def test_profile_total_count(sample_env):
    result = profile_env(sample_env)
    assert result.total == len(sample_env)


def test_profile_empty_count(sample_env):
    result = profile_env(sample_env)
    assert result.empty_count == 1


def test_profile_categories_present(sample_env):
    result = profile_env(sample_env)
    assert "database" in result.categories
    assert "auth" in result.categories
    assert "logging" in result.categories
    assert "feature" in result.categories
    assert "infra" in result.categories


def test_profile_general_category(sample_env):
    result = profile_env(sample_env)
    assert "general" in result.categories
    # APP_NAME and EMPTY_VAR should fall into general
    assert result.categories["general"] >= 1


def test_profile_entries_are_profile_entry(sample_env):
    result = profile_env(sample_env)
    for entry in result.entries:
        assert isinstance(entry, ProfileEntry)


def test_categorize_database():
    assert _categorize("DB_HOST") == "database"
    assert _categorize("POSTGRES_URL") == "database"


def test_categorize_auth():
    assert _categorize("API_KEY") == "auth"
    assert _categorize("JWT_SECRET") == "auth"


def test_categorize_network():
    assert _categorize("SERVICE_HOST") == "network"
    assert _categorize("APP_PORT") == "network"


def test_categorize_general():
    assert _categorize("APP_NAME") == "general"
    assert _categorize("TIMEZONE") == "general"


def test_profile_entry_is_empty_flag():
    result = profile_env({"EMPTY_VAR": "", "FULL_VAR": "value"})
    empty_entries = [e for e in result.entries if e.is_empty]
    full_entries = [e for e in result.entries if not e.is_empty]
    assert len(empty_entries) == 1
    assert len(full_entries) == 1


def test_profile_summary_contains_total(sample_env):
    result = profile_env(sample_env)
    summary = result.summary()
    assert "Total keys" in summary
    assert str(result.total) in summary


def test_profile_summary_contains_empty_count(sample_env):
    result = profile_env(sample_env)
    summary = result.summary()
    assert "Empty values" in summary
    assert "1" in summary


def test_profile_empty_env():
    result = profile_env({})
    assert result.total == 0
    assert result.empty_count == 0
    assert result.categories == {}
