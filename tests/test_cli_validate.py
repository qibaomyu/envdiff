"""Tests for envdiff.cli_validate module."""

import argparse
import os
import pytest

from envdiff.cli_validate import add_validate_args, run_validate


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "test.env"
    p.write_text(
        "APP_NAME=myapp\n"
        "DB_HOST=localhost\n"
        "EMPTY_VAR=\n"
    )
    return str(p)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_validate_args(sub)
    return p


def _run(parser, argv):
    args = parser.parse_args(argv)
    return run_validate(args)


def test_validate_no_issues(env_file, parser):
    code = _run(parser, ["validate", env_file])
    assert code == 0


def test_validate_missing_required_key(env_file, parser):
    code = _run(parser, ["validate", env_file, "--require", "MISSING_KEY"])
    assert code == 1


def test_validate_present_required_key(env_file, parser):
    code = _run(parser, ["validate", env_file, "--require", "APP_NAME"])
    assert code == 0


def test_validate_forbidden_key_present(env_file, parser):
    code = _run(parser, ["validate", env_file, "--forbid", "DB_HOST"])
    assert code == 1


def test_validate_forbidden_key_absent(env_file, parser):
    code = _run(parser, ["validate", env_file, "--forbid", "NOT_THERE"])
    assert code == 0


def test_validate_empty_value_warning(env_file, parser, capsys):
    code = _run(parser, ["validate", env_file, "--no-empty"])
    captured = capsys.readouterr()
    assert "EMPTY_VAR" in captured.out
    assert "WARN" in captured.out
    # warnings alone don't cause error exit
    assert code == 0


def test_validate_file_not_found(parser, capsys):
    code = _run(parser, ["validate", "/nonexistent/path.env"])
    assert code == 2
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_validate_output_ok_message(env_file, parser, capsys):
    _run(parser, ["validate", env_file])
    captured = capsys.readouterr()
    assert "OK" in captured.out
