"""Tests for envdiff.cli_patch."""
import argparse
import json
import textwrap
from pathlib import Path

import pytest

from envdiff.cli_patch import add_patch_args, run_patch


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent("""\
        HOST=localhost
        PORT=5432
        DEBUG=true
    """))
    return p


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    add_patch_args(sub)
    return root


def _run(parser, argv):
    args = parser.parse_args(argv)
    return run_patch(args)


def test_set_new_key(env_file, parser, capsys):
    rc = _run(parser, ["patch", str(env_file), "--set", "REGION=us-east-1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "REGION=us-east-1" in out


def test_set_overwrites_existing_key(env_file, parser, capsys):
    rc = _run(parser, ["patch", str(env_file), "--set", "PORT=9999"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "PORT=9999" in out


def test_no_overwrite_flag_preserves_value(env_file, parser, capsys):
    rc = _run(parser, ["patch", str(env_file), "--set", "PORT=9999", "--no-overwrite"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "PORT=5432" in out
    assert "PORT=9999" not in out


def test_unset_removes_key(env_file, parser, capsys):
    rc = _run(parser, ["patch", str(env_file), "--unset", "DEBUG"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DEBUG" not in out


def test_rename_key(env_file, parser, capsys):
    rc = _run(parser, ["patch", str(env_file), "--rename", "HOST=DB_HOST"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out
    assert "HOST=localhost" not in out


def test_json_output_format(env_file, parser, capsys):
    rc = _run(parser, ["patch", str(env_file), "--set", "X=1", "--format", "json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["X"] == "1"
    assert data["HOST"] == "localhost"


def test_summary_written_to_stderr(env_file, parser, capsys):
    _run(parser, ["patch", str(env_file), "--set", "NEW=val", "--unset", "GHOST"])
    err = capsys.readouterr().err
    assert "applied" in err
    assert "skipped" in err


def test_invalid_set_format_exits(env_file, parser):
    with pytest.raises(SystemExit) as exc:
        _run(parser, ["patch", str(env_file), "--set", "BADFORMAT"])
    assert exc.value.code == 2
