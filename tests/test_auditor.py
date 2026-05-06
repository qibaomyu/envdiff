"""Tests for envdiff.auditor and envdiff.cli_audit."""

from __future__ import annotations

import json
import os

import pytest

from envdiff.auditor import (
    AUDIT_VERSION,
    audit_summary,
    load_audit,
    record_audit,
    save_audit,
)


@pytest.fixture()
def sample_audit():
    return record_audit(
        sources=["a.env", "b.env"],
        env_data={
            "a.env": {"FOO": "1", "BAR": "x"},
            "b.env": {"FOO": "2", "BAZ": "y"},
        },
        result_summary={"has_differences": True, "only_in_a": ["BAR"], "only_in_b": ["BAZ"], "value_differs": ["FOO"]},
        label="ci-check",
    )


def test_record_audit_has_version(sample_audit):
    assert sample_audit["audit_version"] == AUDIT_VERSION


def test_record_audit_has_timestamp(sample_audit):
    assert "timestamp" in sample_audit
    assert sample_audit["timestamp"].endswith("+00:00")


def test_record_audit_stores_label(sample_audit):
    assert sample_audit["label"] == "ci-check"


def test_record_audit_no_label_defaults_empty():
    audit = record_audit(sources=[], env_data={}, result_summary={})
    assert audit["label"] == ""


def test_save_and_load_roundtrip(tmp_path, sample_audit):
    dest = str(tmp_path / "audit.json")
    save_audit(sample_audit, dest)
    loaded = load_audit(dest)
    assert loaded["sources"] == ["a.env", "b.env"]
    assert loaded["label"] == "ci-check"
    assert loaded["result_summary"]["has_differences"] is True


def test_save_creates_parent_dirs(tmp_path, sample_audit):
    dest = str(tmp_path / "nested" / "dir" / "audit.json")
    save_audit(sample_audit, dest)
    assert os.path.exists(dest)


def test_load_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_audit("/nonexistent/audit.json")


def test_load_wrong_version(tmp_path, sample_audit):
    sample_audit["audit_version"] = "99.0"
    dest = str(tmp_path / "bad.json")
    with open(dest, "w") as fh:
        json.dump(sample_audit, fh)
    with pytest.raises(ValueError, match="Unsupported audit version"):
        load_audit(dest)


def test_audit_summary_with_differences(sample_audit):
    result = audit_summary(sample_audit)
    assert "DIFFERENCES FOUND" in result
    assert "ci-check" in result
    assert "a.env" in result


def test_audit_summary_no_differences():
    audit = record_audit(
        sources=["x.env", "y.env"],
        env_data={},
        result_summary={"has_differences": False},
        label="clean",
    )
    result = audit_summary(audit)
    assert "no differences" in result
    assert "clean" in result
