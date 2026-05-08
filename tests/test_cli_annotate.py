"""Tests for envdiff.cli_annotate."""
import argparse
import json
import os
import textwrap

import pytest

from envdiff.cli_annotate import add_annotate_args, run_annotate


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PASSWORD=secret\nDEBUG=true\n")
    return str(p)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_annotate_args(sub)
    return p


def _run(parser, env_file, extra_args=None):
    args = parser.parse_args(["annotate", env_file] + (extra_args or []))
    return run_annotate(args)


def test_no_rules_exits_zero(parser, env_file):
    assert _run(parser, env_file) == 0


def test_with_rules_exits_zero(parser, env_file):
    rc = _run(parser, env_file, ["--rule", "DB_HOST=Database host"])
    assert rc == 0


def test_text_output_shows_summary(parser, env_file, capsys):
    _run(parser, env_file, ["--rule", "DB_HOST=Database host"])
    out = capsys.readouterr().out
    assert "annotated" in out
    assert "unannotated" in out


def test_text_output_shows_comment(parser, env_file, capsys):
    _run(parser, env_file, ["--rule", "DB_HOST=Database host"])
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "Database host" in out


def test_json_output_structure(parser, env_file, capsys):
    _run(parser, env_file, ["--rule", "DB_HOST=hint", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "annotated" in data
    assert "unannotated" in data
    assert any(e["key"] == "DB_HOST" for e in data["annotated"])


def test_dotenv_output_contains_comment(parser, env_file, capsys):
    _run(parser, env_file, ["--rule", "DB_HOST=Database host", "--format", "dotenv"])
    out = capsys.readouterr().out
    assert "# Database host" in out
    assert "DB_HOST=localhost" in out


def test_missing_file_returns_nonzero(parser, tmp_path):
    missing = str(tmp_path / "missing.env")
    rc = _run(parser, missing)
    assert rc == 1


def test_invalid_rule_skipped(parser, env_file, capsys):
    # Rule without '=' should be skipped gracefully
    rc = _run(parser, env_file, ["--rule", "BADRULE"])
    assert rc == 0
    err = capsys.readouterr().err
    assert "BADRULE" in err
