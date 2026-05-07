"""Tests for envdiff.cli_template."""

from __future__ import annotations

import argparse

import pytest

from envdiff.cli_template import add_template_args, run_template


@pytest.fixture()
def tmpl_file(tmp_path):
    p = tmp_path / "app.conf.tmpl"
    p.write_text("HOST={{ HOST }}\nPORT={{ PORT }}\n")
    return p


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("HOST=localhost\nPORT=8080\n")
    return p


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_template_args(sub)
    return p


def _run(parser, argv):
    args = parser.parse_args(argv)
    return run_template(args)


# ---------------------------------------------------------------------------
# Basic rendering
# ---------------------------------------------------------------------------

def test_render_to_stdout(parser, tmpl_file, env_file, capsys):
    code = _run(parser, ["template", str(tmpl_file), "--env", str(env_file)])
    assert code == 0
    captured = capsys.readouterr()
    assert "HOST=localhost" in captured.out
    assert "PORT=8080" in captured.out


def test_render_to_output_file(parser, tmpl_file, env_file, tmp_path):
    out = tmp_path / "rendered.conf"
    code = _run(
        parser,
        ["template", str(tmpl_file), "--env", str(env_file), "--output", str(out)],
    )
    assert code == 0
    content = out.read_text()
    assert "HOST=localhost" in content


# ---------------------------------------------------------------------------
# Missing placeholders
# ---------------------------------------------------------------------------

def test_strict_mode_missing_key_returns_error(parser, tmpl_file, tmp_path, capsys):
    empty_env = tmp_path / "empty.env"
    empty_env.write_text("")
    code = _run(
        parser,
        ["template", str(tmpl_file), "--env", str(empty_env), "--strict"],
    )
    assert code == 1
    assert "HOST" in capsys.readouterr().err


def test_non_strict_uses_default(parser, tmpl_file, tmp_path, capsys):
    empty_env = tmp_path / "empty.env"
    empty_env.write_text("")
    code = _run(
        parser,
        [
            "template",
            str(tmpl_file),
            "--env",
            str(empty_env),
            "--default",
            "UNSET",
        ],
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "HOST=UNSET" in out


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------

def test_missing_template_file_returns_2(parser, tmp_path):
    code = _run(parser, ["template", str(tmp_path / "no.tmpl")])
    assert code == 2


def test_missing_env_file_returns_2(parser, tmpl_file, tmp_path):
    code = _run(
        parser,
        ["template", str(tmpl_file), "--env", str(tmp_path / "no.env")],
    )
    assert code == 2
