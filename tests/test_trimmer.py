"""Tests for envdiff.trimmer and envdiff.cli_trim."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envdiff.trimmer import TrimEntry, TrimResult, trim_env
from envdiff.cli_trim import add_trim_args, run_trim


@pytest.fixture
def sample_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "DB_HOST": "localhost",
        "DB_PASS": "",
        "API_KEY": "   ",
        "SECRET": "<REPLACE_ME>",
        "TOKEN": "${TOKEN}",
        "DEBUG": "true",
        "LEGACY": "CHANGE_ME",
    }


def test_trim_removes_empty_values(sample_env):
    result = trim_env(sample_env)
    assert "DB_PASS" not in result.trimmed
    assert any(e.key == "DB_PASS" and e.reason == "empty" for e in result.removed)


def test_trim_removes_whitespace_only(sample_env):
    result = trim_env(sample_env)
    assert "API_KEY" not in result.trimmed
    assert any(e.key == "API_KEY" and e.reason == "whitespace-only" for e in result.removed)


def test_trim_removes_placeholder_angle_brackets(sample_env):
    result = trim_env(sample_env)
    assert "SECRET" not in result.trimmed
    assert any(e.key == "SECRET" and e.reason == "placeholder" for e in result.removed)


def test_trim_removes_shell_variable_placeholder(sample_env):
    result = trim_env(sample_env)
    assert "TOKEN" not in result.trimmed


def test_trim_removes_change_me(sample_env):
    result = trim_env(sample_env)
    assert "LEGACY" not in result.trimmed


def test_trim_keeps_valid_keys(sample_env):
    result = trim_env(sample_env)
    assert "APP_NAME" in result.trimmed
    assert "DB_HOST" in result.trimmed
    assert "DEBUG" in result.trimmed


def test_trim_has_removals(sample_env):
    result = trim_env(sample_env)
    assert result.has_removals()


def test_trim_no_removals_clean_env():
    env = {"A": "1", "B": "hello"}
    result = trim_env(env)
    assert not result.has_removals()
    assert result.trimmed == env


def test_trim_keep_empty_flag(sample_env):
    result = trim_env(sample_env, remove_empty=False)
    assert "DB_PASS" in result.trimmed


def test_trim_keep_placeholders_flag(sample_env):
    result = trim_env(sample_env, remove_placeholders=False)
    assert "SECRET" in result.trimmed
    assert "TOKEN" in result.trimmed


def test_trim_extra_pattern():
    env = {"KEY": "PENDING", "OTHER": "value"}
    result = trim_env(env, extra_placeholder_patterns=[r"^PENDING$"])
    assert "KEY" not in result.trimmed
    assert "OTHER" in result.trimmed


def test_trim_summary_format(sample_env):
    result = trim_env(sample_env)
    s = result.summary()
    assert "kept" in s
    assert "removed" in s


def test_trim_original_unchanged(sample_env):
    original_copy = dict(sample_env)
    result = trim_env(sample_env)
    assert result.original == original_copy


# --- CLI tests ---

@pytest.fixture
def env_file(tmp_path) -> Path:
    p = tmp_path / "test.env"
    p.write_text(
        "APP=myapp\nEMPTY=\nPLACEHOLDER=<REPLACE_ME>\nGOOD=hello\n"
    )
    return p


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_trim_args(p)
    return p


def _run(parser, env_file, extra_args=None):
    argv = [str(env_file)] + (extra_args or [])
    args = parser.parse_args(argv)
    return run_trim(args)


def test_cli_trim_exits_one_when_removals(env_file, parser):
    rc = _run(parser, env_file)
    assert rc == 1


def test_cli_trim_exits_zero_clean(tmp_path, parser):
    p = tmp_path / "clean.env"
    p.write_text("A=1\nB=2\n")
    rc = _run(parser, p)
    assert rc == 0


def test_cli_trim_json_output(env_file, parser, capsys):
    _run(parser, env_file, ["--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "trimmed" in data
    assert "summary" in data


def test_cli_trim_json_show_removed(env_file, parser, capsys):
    _run(parser, env_file, ["--format", "json", "--show-removed"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "removed" in data
    assert any(e["key"] == "EMPTY" for e in data["removed"])


def test_cli_trim_dotenv_output(env_file, parser, capsys):
    _run(parser, env_file, ["--format", "dotenv"])
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert any(line.startswith("APP=") for line in lines)
    assert not any("EMPTY" in line for line in lines)
