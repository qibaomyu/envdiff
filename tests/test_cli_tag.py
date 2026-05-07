"""Tests for envdiff.cli_tag."""

import argparse
import json
import os
import textwrap
from io import StringIO

import pytest

from envdiff.cli_tag import add_tag_args, run_tag


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        textwrap.dedent(
            """\
            DB_HOST=localhost
            DB_PASSWORD=secret
            AWS_ACCESS_KEY_ID=AKIA123
            APP_DEBUG=true
            """
        )
    )
    return str(p)


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    add_tag_args(p)
    return p


def _run(parser, argv, capsys):
    args = parser.parse_args(argv)
    code = run_tag(args)
    captured = capsys.readouterr()
    return code, captured.out


def test_no_rules_shows_all_keys_untagged(env_file, parser, capsys):
    code, out = _run(parser, [env_file], capsys)
    assert code == 0
    assert "DB_HOST" in out
    assert "(none)" in out


def test_rule_tags_db_keys(env_file, parser, capsys):
    code, out = _run(parser, [env_file, "--rule", r"^DB_=database"], capsys)
    assert code == 0
    assert "DB_HOST  [database]" in out
    assert "DB_PASSWORD  [database]" in out


def test_multiple_tags_in_single_rule(env_file, parser, capsys):
    code, out = _run(
        parser,
        [env_file, "--rule", r"^AWS_=cloud,sensitive"],
        capsys,
    )
    assert code == 0
    assert "cloud" in out
    assert "sensitive" in out


def test_filter_tag_limits_output(env_file, parser, capsys):
    code, out = _run(
        parser,
        [env_file, "--rule", r"^DB_=database", "--filter-tag", "database"],
        capsys,
    )
    assert code == 0
    assert "DB_HOST" in out
    assert "APP_DEBUG" not in out


def test_filter_tag_no_match_shows_message(env_file, parser, capsys):
    code, out = _run(
        parser,
        [env_file, "--filter-tag", "nonexistent"],
        capsys,
    )
    assert code == 0
    assert "No entries" in out


def test_json_output_is_valid(env_file, parser, capsys):
    code, out = _run(
        parser,
        [env_file, "--rule", r"^DB_=database", "--format", "json"],
        capsys,
    )
    assert code == 0
    data = json.loads(out)
    assert isinstance(data, list)
    keys = {item["key"] for item in data}
    assert "DB_HOST" in keys


def test_json_output_contains_tags(env_file, parser, capsys):
    code, out = _run(
        parser,
        [env_file, "--rule", r"^DB_=database", "--format", "json"],
        capsys,
    )
    data = json.loads(out)
    db_host = next(item for item in data if item["key"] == "DB_HOST")
    assert "database" in db_host["tags"]


def test_default_tag_applied_to_unmatched(env_file, parser, capsys):
    code, out = _run(
        parser,
        [
            env_file,
            "--rule", r"^DB_=database",
            "--default-tag", "misc",
            "--format", "json",
        ],
        capsys,
    )
    data = json.loads(out)
    app_debug = next(item for item in data if item["key"] == "APP_DEBUG")
    assert "misc" in app_debug["tags"]
