"""Tests for envdiff.summarizer."""
import pytest
from envdiff.summarizer import EnvSummary, summarize_env, text_summary


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "DB_PASSWORD": "",
        "API_KEY": "secret",
        "API_SECRET": "secret",  # duplicate value with API_KEY
        "LOG_LEVEL": "info",
    }


def test_total_count(sample_env):
    result = summarize_env(sample_env)
    assert result.total == 7


def test_empty_count(sample_env):
    result = summarize_env(sample_env)
    assert result.empty_count == 1


def test_non_empty_count(sample_env):
    result = summarize_env(sample_env)
    assert result.non_empty_count == 6


def test_unique_values(sample_env):
    # "secret" appears twice, so it is NOT unique
    result = summarize_env(sample_env)
    # values: localhost, 5432, mydb, "", secret, secret, info
    # unique (appear once): localhost, 5432, mydb, "", info  -> 5
    assert result.unique_values == 5


def test_duplicate_values(sample_env):
    result = summarize_env(sample_env)
    # only "secret" appears more than once -> 1 duplicate group
    assert result.duplicate_values == 1


def test_longest_key(sample_env):
    result = summarize_env(sample_env)
    assert result.longest_key == "DB_PASSWORD"


def test_shortest_key(sample_env):
    result = summarize_env(sample_env)
    # DB_HOST, DB_PORT, DB_NAME all length 7; API_KEY length 7; LOG_LEVEL 9
    # shortest is any of the 7-char keys
    assert len(result.shortest_key) == 6  # API_KEY is 7, DB_HOST is 7... LOG_LEVEL=9
    # actually shortest: DB_HOST=7, API_KEY=7, DB_PORT=7, DB_NAME=7, LOG_LEVEL=9, DB_PASSWORD=11, API_SECRET=10
    # min length is 7
    assert len(result.shortest_key) == 7


def test_avg_value_length(sample_env):
    result = summarize_env(sample_env)
    total = len("localhost") + len("5432") + len("mydb") + 0 + len("secret") + len("secret") + len("info")
    expected = round(total / 7, 2)
    assert result.avg_value_length == expected


def test_key_lengths_sorted(sample_env):
    result = summarize_env(sample_env)
    assert result.key_lengths == sorted(result.key_lengths)


def test_empty_env_returns_zeros():
    result = summarize_env({})
    assert result.total == 0
    assert result.empty_count == 0
    assert result.unique_values == 0
    assert result.longest_key == ""
    assert result.avg_value_length == 0.0


def test_all_empty_values():
    env = {"A": "", "B": "", "C": ""}
    result = summarize_env(env)
    assert result.empty_count == 3
    assert result.non_empty_count == 0


def test_text_summary_contains_total(sample_env):
    s = summarize_env(sample_env)
    output = text_summary(s)
    assert "Total keys" in output
    assert "7" in output


def test_text_summary_contains_longest_key(sample_env):
    s = summarize_env(sample_env)
    output = text_summary(s)
    assert "DB_PASSWORD" in output


def test_longest_value_key_is_valid_key(sample_env):
    result = summarize_env(sample_env)
    assert result.longest_value_key in sample_env
    max_len = max(len(v) for v in sample_env.values())
    assert len(sample_env[result.longest_value_key]) == max_len
