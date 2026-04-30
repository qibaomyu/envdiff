"""Tests for envdiff.reporter module."""

from __future__ import annotations

import io
import json

import pytest

from envdiff.comparator import EnvDiffResult
from envdiff.reporter import OutputFormat, render


@pytest.fixture()
def diff_result() -> EnvDiffResult:
    return EnvDiffResult(
        only_in_a={"ONLY_A"},
        only_in_b={"ONLY_B"},
        value_differs={"SHARED": ("old_val", "new_val")},
        common_keys={"SHARED", "COMMON"},
    )


@pytest.fixture()
def clean_result() -> EnvDiffResult:
    return EnvDiffResult(
        only_in_a=set(),
        only_in_b=set(),
        value_differs={},
        common_keys={"KEY"},
    )


def test_text_report_contains_labels(diff_result: EnvDiffResult) -> None:
    buf = io.StringIO()
    render(diff_result, label_a="staging", label_b="prod", out=buf)
    output = buf.getvalue()
    assert "staging" in output
    assert "prod" in output


def test_text_report_only_in_a(diff_result: EnvDiffResult) -> None:
    buf = io.StringIO()
    render(diff_result, label_a="A", label_b="B", out=buf)
    assert "ONLY_A" in buf.getvalue()


def test_text_report_only_in_b(diff_result: EnvDiffResult) -> None:
    buf = io.StringIO()
    render(diff_result, label_a="A", label_b="B", out=buf)
    assert "ONLY_B" in buf.getvalue()


def test_text_report_value_differs(diff_result: EnvDiffResult) -> None:
    buf = io.StringIO()
    render(diff_result, label_a="A", label_b="B", out=buf)
    output = buf.getvalue()
    assert "SHARED" in output
    assert "old_val" in output
    assert "new_val" in output


def test_text_report_no_differences(clean_result: EnvDiffResult) -> None:
    buf = io.StringIO()
    render(clean_result, out=buf)
    assert "No differences found" in buf.getvalue()


def test_json_report_structure(diff_result: EnvDiffResult) -> None:
    buf = io.StringIO()
    render(diff_result, label_a="dev", label_b="prod", fmt=OutputFormat.JSON, out=buf)
    data = json.loads(buf.getvalue())
    assert data["targets"] == {"a": "dev", "b": "prod"}
    assert "ONLY_A" in data["only_in_a"]
    assert "ONLY_B" in data["only_in_b"]
    assert data["has_differences"] is True
    assert "SHARED" in data["value_differs"]
    assert data["value_differs"]["SHARED"]["dev"] == "old_val"
    assert data["value_differs"]["SHARED"]["prod"] == "new_val"


def test_json_report_no_differences(clean_result: EnvDiffResult) -> None:
    buf = io.StringIO()
    render(clean_result, fmt=OutputFormat.JSON, out=buf)
    data = json.loads(buf.getvalue())
    assert data["has_differences"] is False
    assert data["only_in_a"] == []
    assert data["only_in_b"] == []
