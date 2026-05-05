"""Tests for the envdiff CLI module."""

import os
import pytest
from unittest.mock import patch

from envdiff.cli import run, build_parser


@pytest.fixture
def env_file_a(tmp_path):
    f = tmp_path / "a.env"
    f.write_text("KEY1=foo\nKEY2=bar\nCOMMON=same\n")
    return str(f)


@pytest.fixture
def env_file_b(tmp_path):
    f = tmp_path / "b.env"
    f.write_text("KEY2=different\nCOMMON=same\nKEY3=baz\n")
    return str(f)


def test_run_two_files_text_output(env_file_a, env_file_b, capsys):
    exit_code = run([env_file_a, env_file_b])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "KEY1" in captured.out
    assert "KEY2" in captured.out
    assert "KEY3" in captured.out


def test_run_exit_code_when_differences(env_file_a, env_file_b):
    exit_code = run([env_file_a, env_file_b, "--exit-code"])
    assert exit_code == 1


def test_run_exit_code_no_differences(tmp_path, capsys):
    f1 = tmp_path / "x.env"
    f2 = tmp_path / "y.env"
    f1.write_text("A=1\n")
    f2.write_text("A=1\n")
    exit_code = run([str(f1), str(f2), "--exit-code"])
    assert exit_code == 0


def test_run_json_format(env_file_a, env_file_b, capsys):
    run([env_file_a, env_file_b, "--format", "json"])
    captured = capsys.readouterr()
    import json
    data = json.loads(captured.out)
    assert "only_in_a" in data
    assert "only_in_b" in data
    assert "value_differs" in data


def test_run_custom_labels(env_file_a, env_file_b, capsys):
    run([env_file_a, env_file_b, "--label-a", "prod", "--label-b", "staging"])
    captured = capsys.readouterr()
    assert "prod" in captured.out
    assert "staging" in captured.out


def test_run_os_env_mode(env_file_a, capsys):
    fake_env = {"KEY1": "foo", "EXTRA": "val"}
    with patch("envdiff.cli.load_from_os_environ", return_value=fake_env):
        exit_code = run([env_file_a, "--os-env"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "os.environ" in captured.out


def test_run_os_env_requires_one_file(env_file_a, env_file_b):
    with pytest.raises(SystemExit):
        run([env_file_a, env_file_b, "--os-env"])


def test_run_two_files_required_without_os_env(env_file_a):
    with pytest.raises(SystemExit):
        run([env_file_a])


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["a.env", "b.env"])
    assert args.output_format == "text"
    assert args.exit_code is False
    assert args.os_env is False
