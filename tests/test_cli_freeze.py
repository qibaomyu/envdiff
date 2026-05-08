"""Tests for envdiff.cli_freeze."""

import argparse
import json
import os
import pytest

from envdiff.cli_freeze import add_freeze_args, run_freeze


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / "test.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=production\n")
    return str(p)


@pytest.fixture()
def freeze_file(tmp_path):
    return str(tmp_path / "env.freeze.json")


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_freeze_args(sub)
    return p


def _run(parser, argv):
    args = parser.parse_args(argv)
    return run_freeze(args)


def test_save_creates_freeze_file(parser, env_file, freeze_file):
    code = _run(parser, ["freeze", "save", env_file, freeze_file])
    assert code == 0
    assert os.path.exists(freeze_file)


def test_save_freeze_file_has_correct_keys(parser, env_file, freeze_file):
    _run(parser, ["freeze", "save", env_file, freeze_file])
    with open(freeze_file) as fh:
        data = json.load(fh)
    assert data["env"]["DB_HOST"] == "localhost"
    assert data["env"]["DB_PORT"] == "5432"


def test_save_with_label(parser, env_file, freeze_file):
    _run(parser, ["freeze", "save", env_file, freeze_file, "--label", "baseline"])
    with open(freeze_file) as fh:
        data = json.load(fh)
    assert data["label"] == "baseline"


def test_save_with_specific_keys(parser, env_file, freeze_file):
    _run(parser, ["freeze", "save", env_file, freeze_file, "--keys", "DB_HOST"])
    with open(freeze_file) as fh:
        data = json.load(fh)
    assert "DB_HOST" in data["env"]
    assert "DB_PORT" not in data["env"]


def test_check_no_violations_exits_zero(parser, env_file, freeze_file):
    _run(parser, ["freeze", "save", env_file, freeze_file])
    code = _run(parser, ["freeze", "check", freeze_file, env_file])
    assert code == 0


def test_check_violation_exits_one(parser, env_file, freeze_file, tmp_path):
    _run(parser, ["freeze", "save", env_file, freeze_file])
    # Write a different env
    changed = tmp_path / "changed.env"
    changed.write_text("DB_HOST=remotehost\nDB_PORT=5432\nAPP_ENV=production\n")
    code = _run(parser, ["freeze", "check", freeze_file, str(changed)])
    assert code == 1


def test_check_missing_freeze_file_exits_two(parser, env_file, tmp_path):
    missing = str(tmp_path / "no_such.freeze.json")
    code = _run(parser, ["freeze", "check", missing, env_file])
    assert code == 2


def test_check_output_contains_violation_key(parser, env_file, freeze_file, tmp_path, capsys):
    _run(parser, ["freeze", "save", env_file, freeze_file])
    changed = tmp_path / "changed.env"
    changed.write_text("DB_HOST=other\nDB_PORT=5432\nAPP_ENV=production\n")
    _run(parser, ["freeze", "check", freeze_file, str(changed)])
    out = capsys.readouterr().out
    assert "DB_HOST" in out
