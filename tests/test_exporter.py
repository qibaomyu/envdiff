"""Tests for envdiff.exporter module."""

import json
import csv
import io
from pathlib import Path

import pytest

from envdiff.comparator import compare_envs
from envdiff.exporter import ExportFormat, export


@pytest.fixture()
def diff_result():
    env_a = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true", "ONLY_A": "yes"}
    env_b = {"HOST": "prod.example.com", "PORT": "8080", "DEBUG": "false", "ONLY_B": "no"}
    return compare_envs(env_a, env_b)


def test_export_csv_headers(diff_result):
    content = export(diff_result, ExportFormat.CSV, label_a="staging", label_b="prod")
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    assert header == ["key", "status", "staging", "prod"]


def test_export_csv_only_in_a(diff_result):
    content = export(diff_result, ExportFormat.CSV)
    rows = list(csv.reader(io.StringIO(content)))
    statuses = {row[0]: row[1] for row in rows[1:]}
    assert statuses["ONLY_A"] == "only_in_a"


def test_export_csv_only_in_b(diff_result):
    content = export(diff_result, ExportFormat.CSV)
    rows = list(csv.reader(io.StringIO(content)))
    statuses = {row[0]: row[1] for row in rows[1:]}
    assert statuses["ONLY_B"] == "only_in_b"


def test_export_csv_value_differs(diff_result):
    content = export(diff_result, ExportFormat.CSV)
    rows = list(csv.reader(io.StringIO(content)))
    statuses = {row[0]: row[1] for row in rows[1:]}
    assert statuses["HOST"] == "value_differs"
    assert statuses["DEBUG"] == "value_differs"


def test_export_csv_identical(diff_result):
    content = export(diff_result, ExportFormat.CSV)
    rows = list(csv.reader(io.StringIO(content)))
    statuses = {row[0]: row[1] for row in rows[1:]}
    assert statuses["PORT"] == "identical"


def test_export_json_structure(diff_result):
    content = export(diff_result, ExportFormat.JSON, label_a="a", label_b="b")
    data = json.loads(content)
    assert "only_in_a" in data
    assert "only_in_b" in data
    assert "value_differs" in data
    assert "identical" in data
    assert data["labels"] == {"a": "a", "b": "b"}


def test_export_json_value_differs_contains_both(diff_result):
    content = export(diff_result, ExportFormat.JSON, label_a="env1", label_b="env2")
    data = json.loads(content)
    assert "HOST" in data["value_differs"]
    assert "env1" in data["value_differs"]["HOST"]
    assert "env2" in data["value_differs"]["HOST"]


def test_export_dotenv_contains_conflict_comment(diff_result):
    content = export(diff_result, ExportFormat.DOTENV)
    assert "# CONFLICT: HOST" in content
    assert "# CONFLICT: DEBUG" in content


def test_export_dotenv_uses_env_a_value(diff_result):
    content = export(diff_result, ExportFormat.DOTENV)
    assert "HOST=localhost" in content


def test_export_dotenv_only_b_commented(diff_result):
    content = export(diff_result, ExportFormat.DOTENV)
    assert "# only_in_b: ONLY_B=no" in content


def test_export_writes_to_file(tmp_path, diff_result):
    out = tmp_path / "result.csv"
    export(diff_result, ExportFormat.CSV, output_path=out)
    assert out.exists()
    assert "key,status" in out.read_text()


def test_export_invalid_format_raises(diff_result):
    with pytest.raises((ValueError, AttributeError)):
        export(diff_result, "xml")  # type: ignore
