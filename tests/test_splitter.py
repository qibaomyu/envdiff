"""Tests for envdiff.splitter."""
import pytest
from envdiff.splitter import SplitBucket, SplitResult, split_env


@pytest.fixture()
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET": "secret",
        "APP_NAME": "envdiff",
        "APP_ENV": "production",
        "UNRELATED": "value",
    }


def test_split_by_prefix_creates_buckets(sample_env):
    result = split_env(sample_env, [("database", "DB_"), ("aws", "AWS_")])
    assert "database" in result.bucket_names()
    assert "aws" in result.bucket_names()


def test_split_db_keys_land_in_database_bucket(sample_env):
    result = split_env(sample_env, [("database", "DB_"), ("aws", "AWS_")])
    assert "DB_HOST" in result.buckets["database"].env
    assert "DB_PORT" in result.buckets["database"].env


def test_split_aws_keys_land_in_aws_bucket(sample_env):
    result = split_env(sample_env, [("database", "DB_"), ("aws", "AWS_")])
    assert "AWS_ACCESS_KEY" in result.buckets["aws"].env
    assert "AWS_SECRET" in result.buckets["aws"].env


def test_unmatched_keys_in_remainder(sample_env):
    result = split_env(sample_env, [("database", "DB_"), ("aws", "AWS_")])
    assert "UNRELATED" in result.remainder
    assert "APP_NAME" in result.remainder
    assert "APP_ENV" in result.remainder


def test_keep_remainder_false_discards_unmatched(sample_env):
    result = split_env(
        sample_env,
        [("database", "DB_"), ("aws", "AWS_")],
        keep_remainder=False,
    )
    assert result.remainder == {}


def test_first_rule_wins_on_overlap():
    env = {"DB_AWS_KEY": "val"}
    result = split_env(env, [("database", "DB_"), ("aws", "AWS_")])
    assert "DB_AWS_KEY" in result.buckets["database"].env
    assert "DB_AWS_KEY" not in result.buckets["aws"].env


def test_regex_mode(sample_env):
    result = split_env(
        sample_env,
        [("app", r"^APP_"), ("infra", r"(DB|AWS)_")],
        use_regex=True,
    )
    assert "APP_NAME" in result.buckets["app"].env
    assert "DB_HOST" in result.buckets["infra"].env
    assert "AWS_SECRET" in result.buckets["infra"].env


def test_bucket_len(sample_env):
    result = split_env(sample_env, [("database", "DB_")])
    assert len(result.buckets["database"]) == 2


def test_summary_contains_bucket_names(sample_env):
    result = split_env(sample_env, [("database", "DB_"), ("aws", "AWS_")])
    summary = result.summary()
    assert "database" in summary
    assert "aws" in summary
    assert "remainder" in summary


def test_empty_env_returns_empty_buckets():
    result = split_env({}, [("database", "DB_")])
    assert len(result.buckets["database"]) == 0
    assert result.remainder == {}


def test_no_rules_all_keys_in_remainder(sample_env):
    result = split_env(sample_env, [])
    assert result.remainder == sample_env
    assert result.buckets == {}
