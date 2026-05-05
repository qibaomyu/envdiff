"""Tests for envdiff.cli (including filter integration)."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envdiff.cli import build_parser, run


@pytest.fixture()
def env_file_a(tmp_path: Path) -> Path:
    p = tmp_path / "a.env"
    p.write_text(
        textwrap.dedent(
            """\
            APP_HOST=localhost
            APP_PORT=8080
            DB_PASSWORD=secret
            LOG_LEVEL=DEBUG
            """
        )
    )
    return p


@pytest.fixture()
def env_file_b(tmp_path: Path) -> Path:
    p = tmp_path / "b.env"
    p.write_text(
        textwrap.dedent(
            """\
            APP_HOST=prod.example.com
            APP_PORT=8080
            DB_PASSWORD=topsecret
            LOG_LEVEL=WARNING
            """
        )
    )
    return p


def test_run_two_files_text_output(env_file_a, env_file_b, capsys):
    code = run([str(env_file_a), str(env_file_b)])
    captured = capsys.readouterr()
    assert "APP_HOST" in captured.out
    assert code == 1


def test_run_exit_code_when_differences(env_file_a, env_file_b):
    assert run([str(env_file_a), str(env_file_b)]) == 1


def test_run_exit_code_no_differences(tmp_path):
    f = tmp_path / "same.env"
    f.write_text("KEY=value\n")
    assert run([str(f), str(f)]) == 0


def test_run_with_include_filter(env_file_a, env_file_b, capsys):
    code = run([str(env_file_a), str(env_file_b), "--include", "APP_*"])
    captured = capsys.readouterr()
    assert "APP_HOST" in captured.out
    assert "DB_PASSWORD" not in captured.out
    assert code == 1


def test_run_with_exclude_filter(env_file_a, env_file_b, capsys):
    code = run([str(env_file_a), str(env_file_b), "--exclude", "*PASSWORD"])
    captured = capsys.readouterr()
    assert "DB_PASSWORD" not in captured.out


def test_run_with_prefix_filter(env_file_a, env_file_b, capsys):
    run([str(env_file_a), str(env_file_b), "--prefix", "APP_"])
    captured = capsys.readouterr()
    assert "DB_PASSWORD" not in captured.out
    assert "APP_HOST" in captured.out


def test_run_with_regex_filter(env_file_a, env_file_b, capsys):
    run([str(env_file_a), str(env_file_b), "--regex", r"^LOG_"])
    captured = capsys.readouterr()
    assert "LOG_LEVEL" in captured.out
    assert "APP_HOST" not in captured.out


def test_run_with_custom_labels(env_file_a, env_file_b, capsys):
    run([
        str(env_file_a), str(env_file_b),
        "--label", "staging",
        "--label", "production",
    ])
    captured = capsys.readouterr()
    assert "staging" in captured.out
    assert "production" in captured.out


def test_run_requires_two_files():
    with pytest.raises(SystemExit) as exc_info:
        run(["only_one.env"])
    assert exc_info.value.code != 0


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["a.env", "b.env"])
    assert args.format == "text"
    assert args.include_patterns is None
    assert args.exclude_patterns is None
    assert args.prefix is None
    assert args.regex is None
