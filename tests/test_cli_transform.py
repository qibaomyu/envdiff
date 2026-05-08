"""Tests for envdiff.cli_transform."""

import argparse
import json
import os
import textwrap

import pytest

from envdiff.cli_transform import add_transform_args, run_transform


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        textwrap.dedent("""\
            APP_ENV=production
            DEBUG=FALSE
            DB_HOST=  localhost  
            SECRET='topsecret'
        """)
    )
    return str(p)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_transform_args(sub)
    return p


def _run(parser, argv):
    args = parser.parse_args(argv)
    return run_transform(args)


def test_default_strip_rule(parser, env_file, capsys):
    rc = _run(parser, ["transform", env_file, "--rules", "strip"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "localhost" in out
    # stripped value should not have surrounding spaces
    assert "  localhost  " not in out


def test_uppercase_rule(parser, env_file, capsys):
    rc = _run(parser, ["transform", env_file, "--rules", "uppercase"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "PRODUCTION" in out


def test_only_changed_flag(parser, env_file, capsys):
    rc = _run(parser, ["transform", env_file, "--rules", "strip", "--only-changed"])
    assert rc == 0
    out = capsys.readouterr().out
    # Only DB_HOST had surrounding spaces, so only it should appear
    assert "DB_HOST" in out
    assert "APP_ENV" not in out


def test_json_format(parser, env_file, capsys):
    rc = _run(parser, ["transform", env_file, "--rules", "uppercase", "--format", "json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["APP_ENV"] == "PRODUCTION"
    assert data["DEBUG"] == "FALSE"


def test_keys_filter(parser, env_file, capsys):
    rc = _run(parser, ["transform", env_file, "--rules", "uppercase", "--keys", "DEBUG"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DEBUG" in out
    # APP_ENV should not be in the transformed output section
    assert "PRODUCTION" not in out


def test_unknown_rule_returns_nonzero(parser, env_file, capsys):
    rc = _run(parser, ["transform", env_file, "--rules", "bogus_rule"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "Error" in err


def test_missing_file_returns_nonzero(parser, tmp_path, capsys):
    rc = _run(parser, ["transform", str(tmp_path / "nope.env")])
    assert rc == 1
    err = capsys.readouterr().err
    assert "not found" in err


def test_summary_line_in_text_output(parser, env_file, capsys):
    rc = _run(parser, ["transform", env_file, "--rules", "strip"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "transformed" in out
