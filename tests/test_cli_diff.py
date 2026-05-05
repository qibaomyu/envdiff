"""Tests for envdiff.cli_diff subcommand."""
import argparse
import json
import os
import pytest

from envdiff.cli_diff import add_diff_args, run_diff


@pytest.fixture
def before_file(tmp_path):
    p = tmp_path / "before.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n")
    return str(p)


@pytest.fixture
def after_file(tmp_path):
    p = tmp_path / "after.env"
    p.write_text("DB_HOST=prod.db\nDB_PORT=5432\nNEW_KEY=hello\n")
    return str(p)


@pytest.fixture
def snapshot_file(tmp_path):
    p = tmp_path / "snap.json"
    data = {
        "version": "1",
        "meta": {},
        "env": {"DB_HOST": "snap.host", "DB_PORT": "5432"},
    }
    p.write_text(json.dumps(data))
    return str(p)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_diff_args(sub)
    return p


def test_run_diff_detects_changes(before_file, after_file, parser):
    args = parser.parse_args(["diff", before_file, after_file])
    code = run_diff(args)
    assert code == 1


def test_run_diff_no_changes(before_file, parser):
    args = parser.parse_args(["diff", before_file, before_file])
    code = run_diff(args)
    assert code == 0


def test_run_diff_output_contains_added(before_file, after_file, parser, capsys):
    args = parser.parse_args(["diff", before_file, after_file])
    run_diff(args)
    captured = capsys.readouterr()
    assert "NEW_KEY" in captured.out


def test_run_diff_output_contains_removed(before_file, after_file, parser, capsys):
    args = parser.parse_args(["diff", before_file, after_file])
    run_diff(args)
    captured = capsys.readouterr()
    assert "SECRET" in captured.out


def test_run_diff_include_unchanged(before_file, after_file, parser, capsys):
    args = parser.parse_args(["diff", "--include-unchanged", before_file, after_file])
    run_diff(args)
    captured = capsys.readouterr()
    assert "DB_PORT" in captured.out


def test_run_diff_custom_labels(before_file, after_file, parser, capsys):
    args = parser.parse_args(
        ["diff", "--label-before", "v1", "--label-after", "v2", before_file, after_file]
    )
    run_diff(args)
    captured = capsys.readouterr()
    assert "v1 -> v2" in captured.out


def test_run_diff_missing_file_returns_2(before_file, parser, capsys):
    args = parser.parse_args(["diff", before_file, "/nonexistent/path.env"])
    code = run_diff(args)
    assert code == 2
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_run_diff_loads_snapshot(before_file, snapshot_file, parser, capsys):
    args = parser.parse_args(["diff", before_file, snapshot_file])
    code = run_diff(args)
    # snap has different DB_HOST and missing SECRET/NEW_KEY relative to before
    assert code == 1
