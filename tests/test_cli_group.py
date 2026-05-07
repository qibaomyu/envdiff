"""Tests for envdiff.cli_group."""

import argparse
import json
import pytest

from envdiff.cli_group import add_group_args, run_group


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "AWS_KEY=AKIA\n"
        "AWS_SECRET=s3cr3t\n"
        "PORT=8080\n"
    )
    return str(f)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_group_args(sub)
    return p


def _run(parser, argv):
    args = parser.parse_args(argv)
    return args.func(args)


def test_group_prefix_text_output(parser, env_file, capsys):
    rc = _run(parser, ["group", env_file])
    assert rc == 0
    out = capsys.readouterr().out
    assert "[DB]" in out
    assert "[AWS]" in out


def test_group_prefix_json_output(parser, env_file, capsys):
    rc = _run(parser, ["group", env_file, "--format", "json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "DB" in data
    assert "DB_HOST" in data["DB"]


def test_group_prefix_ungrouped_shown(parser, env_file, capsys):
    _run(parser, ["group", env_file])
    out = capsys.readouterr().out
    assert "__ungrouped__" in out
    assert "PORT" in out


def test_group_min_group_size_merges(parser, env_file, capsys):
    # AWS has 2 keys; with min_group_size=3 they should become ungrouped
    _run(parser, ["group", env_file, "--min-group-size", "3"])
    out = capsys.readouterr().out
    assert "[AWS]" not in out
    assert "AWS_KEY" in out  # present but under __ungrouped__


def test_group_regex_strategy(parser, env_file, capsys):
    rc = _run(
        parser,
        ["group", env_file, "--by", "regex", "--pattern", "database=^DB_"],
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "[database]" in out
    assert "DB_HOST" in out


def test_group_regex_json(parser, env_file, capsys):
    _run(
        parser,
        [
            "group", env_file,
            "--by", "regex",
            "--pattern", "cloud=^AWS_",
            "--format", "json",
        ],
    )
    data = json.loads(capsys.readouterr().out)
    assert "cloud" in data
    assert "AWS_KEY" in data["cloud"]


def test_group_returns_zero_on_success(parser, env_file):
    rc = _run(parser, ["group", env_file])
    assert rc == 0
