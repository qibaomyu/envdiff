"""Tests for envdiff.cli_diff_summary."""
from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import pytest

from envdiff.cli_diff_summary import add_diff_summary_args, run_diff_summary


@pytest.fixture()
def before_file(tmp_path: Path) -> Path:
    p = tmp_path / "before.env"
    p.write_text(textwrap.dedent("""\
        DB_HOST=localhost
        DB_PORT=5432
        OLD_KEY=gone
        SHARED=same
    """))
    return p


@pytest.fixture()
def after_file(tmp_path: Path) -> Path:
    p = tmp_path / "after.env"
    p.write_text(textwrap.dedent("""\
        DB_HOST=prod.db
        DB_PORT=5432
        NEW_KEY=hello
        SHARED=same
    """))
    return p


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_diff_summary_args(sub)
    return p


def _run(parser, args, capsys):
    ns = parser.parse_args(args)
    code = ns.func(ns)
    captured = capsys.readouterr()
    return code, captured.out


def test_text_output_contains_total(before_file, after_file, parser, capsys):
    code, out = _run(parser, ["diff-summary", str(before_file), str(after_file)], capsys)
    assert "Total keys" in out
    assert code == 0


def test_text_output_shows_added(before_file, after_file, parser, capsys):
    _, out = _run(parser, ["diff-summary", str(before_file), str(after_file)], capsys)
    assert "Added" in out


def test_json_output_is_valid(before_file, after_file, parser, capsys):
    _, out = _run(
        parser, ["diff-summary", str(before_file), str(after_file), "--format", "json"], capsys
    )
    data = json.loads(out)
    assert "total" in data
    assert "added" in data
    assert "removed" in data


def test_json_counts_correct(before_file, after_file, parser, capsys):
    _, out = _run(
        parser, ["diff-summary", str(before_file), str(after_file), "--format", "json"], capsys
    )
    data = json.loads(out)
    assert data["added"] == 1
    assert data["removed"] == 1
    assert data["modified"] == 1
    assert data["unchanged"] == 2


def test_exit_code_one_when_changes(before_file, after_file, parser, capsys):
    code, _ = _run(
        parser, ["diff-summary", str(before_file), str(after_file), "--exit-code"], capsys
    )
    assert code == 1


def test_exit_code_zero_when_identical(before_file, tmp_path, parser, capsys):
    same = tmp_path / "same.env"
    same.write_text(Path(before_file).read_text())
    code, _ = _run(
        parser, ["diff-summary", str(before_file), str(same), "--exit-code"], capsys
    )
    assert code == 0
