"""Tests for envdiff.annotator."""
import pytest
from envdiff.annotator import (
    AnnotationEntry,
    AnnotationResult,
    annotate_env,
    render_annotated_dotenv,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "APP_PORT": "8080",
        "DEBUG": "true",
    }


@pytest.fixture
def rules():
    return {
        "DB_HOST": "Database hostname",
        "DB_PASSWORD": "Database password — keep secret",
        "APP_PORT": "HTTP port the application listens on",
    }


def test_annotated_entries_count(sample_env, rules):
    result = annotate_env(sample_env, rules)
    assert len(result.entries) == 3


def test_unannotated_keys(sample_env, rules):
    result = annotate_env(sample_env, rules)
    assert "DEBUG" in result.unannotated
    assert len(result.unannotated) == 1


def test_by_key_returns_entry(sample_env, rules):
    result = annotate_env(sample_env, rules)
    entry = result.by_key("DB_HOST")
    assert entry is not None
    assert entry.comment == "Database hostname"
    assert entry.value == "localhost"


def test_by_key_missing_returns_none(sample_env, rules):
    result = annotate_env(sample_env, rules)
    assert result.by_key("NONEXISTENT") is None


def test_has_annotations_true(sample_env, rules):
    result = annotate_env(sample_env, rules)
    assert result.has_annotations() is True


def test_has_annotations_false_when_no_rules(sample_env):
    result = annotate_env(sample_env, {})
    assert result.has_annotations() is False


def test_summary_string(sample_env, rules):
    result = annotate_env(sample_env, rules)
    summary = result.summary()
    assert "3 annotated" in summary
    assert "1 unannotated" in summary
    assert "4" in summary


def test_empty_env_produces_empty_result():
    result = annotate_env({}, {"DB_HOST": "hint"})
    assert result.entries == []
    assert result.unannotated == []


def test_render_dotenv_contains_comment(sample_env, rules):
    result = annotate_env(sample_env, rules)
    output = render_annotated_dotenv(result)
    assert "# Database hostname" in output
    assert "DB_HOST=localhost" in output


def test_render_dotenv_unannotated_key_present(sample_env, rules):
    result = annotate_env(sample_env, rules)
    output = render_annotated_dotenv(result)
    assert "DEBUG=" in output


def test_annotation_entry_repr():
    entry = AnnotationEntry(key="K", value="v", comment="a note")
    assert "K" in repr(entry)
    assert "a note" in repr(entry)
