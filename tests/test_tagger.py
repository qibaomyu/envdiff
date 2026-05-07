"""Tests for envdiff.tagger."""

import pytest
from envdiff.tagger import TagEntry, TaggedEnv, tag_env


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY_ID": "AKIA123",
        "APP_DEBUG": "true",
        "CACHE_TTL": "300",
    }


@pytest.fixture()
def rules() -> dict:
    return {
        r"^DB_": ["database"],
        r"PASSWORD|SECRET|KEY": ["sensitive"],
        r"^AWS_": ["cloud", "sensitive"],
    }


def test_tag_env_returns_tagged_env(sample_env, rules):
    result = tag_env(sample_env, rules)
    assert isinstance(result, TaggedEnv)
    assert len(result.entries) == len(sample_env)


def test_db_host_tagged_database(sample_env, rules):
    result = tag_env(sample_env, rules)
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert "database" in entry.tags
    assert "sensitive" not in entry.tags


def test_db_password_tagged_database_and_sensitive(sample_env, rules):
    result = tag_env(sample_env, rules)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert "database" in entry.tags
    assert "sensitive" in entry.tags


def test_aws_key_tagged_cloud_and_sensitive(sample_env, rules):
    result = tag_env(sample_env, rules)
    entry = next(e for e in result.entries if e.key == "AWS_ACCESS_KEY_ID")
    assert "cloud" in entry.tags
    assert "sensitive" in entry.tags


def test_unmatched_key_no_tags_by_default(sample_env, rules):
    result = tag_env(sample_env, rules)
    entry = next(e for e in result.entries if e.key == "APP_DEBUG")
    assert entry.tags == []


def test_unmatched_key_receives_default_tags(sample_env, rules):
    result = tag_env(sample_env, rules, default_tags=["misc"])
    entry = next(e for e in result.entries if e.key == "APP_DEBUG")
    assert entry.tags == ["misc"]


def test_by_tag_filters_correctly(sample_env, rules):
    result = tag_env(sample_env, rules)
    sensitive = result.by_tag("sensitive")
    keys = {e.key for e in sensitive}
    assert "DB_PASSWORD" in keys
    assert "AWS_ACCESS_KEY_ID" in keys
    assert "DB_HOST" not in keys


def test_all_tags_sorted_and_unique(sample_env, rules):
    result = tag_env(sample_env, rules)
    tags = result.all_tags()
    assert tags == sorted(set(tags))
    assert "database" in tags
    assert "sensitive" in tags
    assert "cloud" in tags


def test_summary_counts(sample_env, rules):
    result = tag_env(sample_env, rules)
    s = result.summary()
    assert s["database"] == 2  # DB_HOST, DB_PASSWORD
    assert s["sensitive"] == 2  # DB_PASSWORD, AWS_ACCESS_KEY_ID
    assert s["cloud"] == 1  # AWS_ACCESS_KEY_ID


def test_empty_env_returns_empty_tagged_env(rules):
    result = tag_env({}, rules)
    assert result.entries == []
    assert result.all_tags() == []


def test_no_rules_all_untagged(sample_env):
    result = tag_env(sample_env, {})
    for entry in result.entries:
        assert entry.tags == []
