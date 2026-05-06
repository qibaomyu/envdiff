"""Tests for envdiff.cli_lint."""

import argparse
import pytest
from pathlib import Path

from envdiff.cli_lint import add_lint_args, run_lint


@pytest.fixture
def clean_env_file(tmp_path: Path) -> Path:
    p = tmp_path / "clean.env"
    p.write_text("DATABASE_URL=postgres://localhost/db\nAPP_PORT=8080\n")
    return p


@pytest.fixture
def dirty_env_file(tmp_path: Path) -> Path:
    p = tmp_path / "dirty.env"
    p.write_text("badKey=value\nEMPTY=\n1INVALID=oops\n")
    return p


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_lint_args(sub)
    return p


def _run(parser: argparse.ArgumentParser, *args: str) -> int:
    ns = parser.parse_args(args)
    return ns.func(ns)


def test_clean_file_exits_zero(parser, clean_env_file):
    code = _run(parser, "lint", str(clean_env_file))
    assert code == 0


def test_dirty_file_exits_one(parser, dirty_env_file):
    code = _run(parser, "lint", str(dirty_env_file))
    assert code == 1


def test_missing_file_exits_two(parser, tmp_path):
    code = _run(parser, "lint", str(tmp_path / "no_such.env"))
    assert code == 2


def test_strict_mode_exits_one_on_warnings(parser, tmp_path):
    p = tmp_path / "warn.env"
    p.write_text("lowercase_key=value\n")
    code = _run(parser, "lint", "--strict", str(p))
    assert code == 1


def test_no_strict_exits_zero_on_warnings_only(parser, tmp_path):
    p = tmp_path / "warn.env"
    p.write_text("lowercase_key=value\n")
    code = _run(parser, "lint", str(p))
    assert code == 0


def test_allow_lowercase_suppresses_w001(parser, tmp_path):
    p = tmp_path / "lower.env"
    p.write_text("mykey=value\n")
    # without --allow-lowercase there's a warning but no error → exit 0
    code_default = _run(parser, "lint", str(p))
    assert code_default == 0
    # with --strict it would exit 1 without allow-lowercase
    code_strict = _run(parser, "lint", "--strict", str(p))
    assert code_strict == 1
    # with both flags it should be 0
    code_both = _run(parser, "lint", "--strict", "--allow-lowercase", str(p))
    assert code_both == 0


def test_add_lint_args_registers_subcommand():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_lint_args(sub)
    ns = p.parse_args(["lint", "some.env"])
    assert ns.file == "some.env"
    assert ns.func is run_lint
