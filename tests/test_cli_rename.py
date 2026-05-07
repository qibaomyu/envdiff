"""Tests for envdiff.cli_rename."""

import argparse
import json
import os
import pytest

from envdiff.cli_rename import add_rename_args, run_rename


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_SECRET=s3cr3t\n")
    return str(p)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    add_rename_args(p)
    return p


def _run(parser, argv, capsys=None):
    args = parser.parse_args(argv)
    code = run_rename(args)
    return code


def test_basic_rename_text_output(env_file, parser, capsys):
    args = parser.parse_args([env_file, "--rename", "DB_HOST=DATABASE_HOST"])
    code = run_rename(args)
    captured = capsys.readouterr()
    assert "DB_HOST -> DATABASE_HOST" in captured.out
    assert code == 0


def test_missing_key_returns_nonzero(env_file, parser, capsys):
    args = parser.parse_args([env_file, "--rename", "MISSING=NEW"])
    code = run_rename(args)
    assert code == 1


def test_dotenv_format_output(env_file, parser, capsys):
    args = parser.parse_args([env_file, "--rename", "DB_HOST=DATABASE_HOST", "--format", "dotenv"])
    code = run_rename(args)
    captured = capsys.readouterr()
    assert "DATABASE_HOST=localhost" in captured.out
    assert "DB_HOST=" not in captured.out


def test_json_format_output(env_file, parser, capsys):
    args = parser.parse_args([env_file, "--rename", "DB_PORT=DATABASE_PORT", "--format", "json"])
    run_rename(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "DATABASE_PORT" in data
    assert "DB_PORT" not in data


def test_mapping_file(env_file, parser, tmp_path, capsys):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(json.dumps({"DB_HOST": "DATABASE_HOST"}))
    args = parser.parse_args([env_file, "--mapping", str(mapping_file)])
    code = run_rename(args)
    captured = capsys.readouterr()
    assert "DATABASE_HOST" in captured.out
    assert code == 0


def test_no_rules_returns_error(env_file, parser, capsys):
    args = parser.parse_args([env_file])
    code = run_rename(args)
    captured = capsys.readouterr()
    assert "no rename rules" in captured.err
    assert code == 1


def test_missing_env_file(parser, capsys):
    args = parser.parse_args(["/nonexistent/.env", "--rename", "A=B"])
    code = run_rename(args)
    assert code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err


def test_quiet_flag_suppresses_summary(env_file, parser, capsys):
    args = parser.parse_args([env_file, "--rename", "DB_HOST=DATABASE_HOST", "--quiet"])
    run_rename(args)
    captured = capsys.readouterr()
    assert "renamed" not in captured.out or "key(s) renamed" not in captured.out
