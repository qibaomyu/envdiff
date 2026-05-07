"""Tests for envdiff.cli_mask."""

import argparse
import os
import textwrap

import pytest

from envdiff.cli_mask import add_mask_args, run_mask


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        textwrap.dedent("""\
            APP_NAME=envdiff
            DB_PASSWORD=supersecret
            API_KEY=abc123xyz
            PORT=8080
        """)
    )
    return str(p)


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    subs = p.add_subparsers()
    add_mask_args(subs)
    return p


def _run(parser, argv, capsys):
    args = parser.parse_args(argv)
    code = args.func(args)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_auto_detects_sensitive_keys(env_file, parser, capsys):
    code, out, _ = _run(parser, ["mask", env_file], capsys)
    assert code == 0
    assert "DB_PASSWORD=***" in out
    assert "API_KEY=***" in out


def test_plain_keys_not_masked(env_file, parser, capsys):
    code, out, _ = _run(parser, ["mask", env_file], capsys)
    assert "APP_NAME=envdiff" in out
    assert "PORT=8080" in out


def test_explicit_keys_override_auto(env_file, parser, capsys):
    code, out, _ = _run(parser, ["mask", env_file, "--keys", "PORT"], capsys)
    assert "PORT=***" in out
    # DB_PASSWORD not in --keys, so it should appear unmasked
    assert "DB_PASSWORD=supersecret" in out


def test_partial_flag_reveals_suffix(env_file, parser, capsys):
    code, out, _ = _run(parser, ["mask", env_file, "--partial"], capsys)
    # API_KEY=abc123xyz → partial should show ***6xyz or similar ending in xyz
    assert "API_KEY" in out
    line = [l for l in out.splitlines() if l.startswith("API_KEY")][0]
    assert line.endswith("xyz")


def test_custom_mask_string(env_file, parser, capsys):
    code, out, _ = _run(parser, ["mask", env_file, "--mask", "[REDACTED]"], capsys)
    assert "DB_PASSWORD=[REDACTED]" in out


def test_summary_flag_prints_summary(env_file, parser, capsys):
    code, out, _ = _run(parser, ["mask", env_file, "--summary"], capsys)
    assert "keys masked" in out


def test_missing_file_returns_error(tmp_path, parser, capsys):
    code, _, err = _run(parser, ["mask", str(tmp_path / "nope.env")], capsys)
    assert code == 1
    assert "not found" in err
