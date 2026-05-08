"""Tests for envdiff.cli_alias."""
import argparse
import json
import pytest

from envdiff.cli_alias import add_alias_args, run_alias


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "APP_ENV=production\n"
        "LOG_LEVEL=info\n"
    )
    return str(p)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    add_alias_args(p)
    return p


def _run(parser, env_file, extra_args=None):
    args = parser.parse_args([env_file] + (extra_args or []))
    return run_alias(args)


def test_text_output_shows_aliased_count(env_file, parser, capsys):
    rc = _run(parser, env_file, ["--alias", "DB_HOST=database_host"])
    out = capsys.readouterr().out
    assert "Aliased: 1" in out
    assert rc == 0


def test_text_output_shows_missing_in_summary(env_file, parser, capsys):
    _run(parser, env_file, ["--alias", "GHOST=ghost_alias"])
    out = capsys.readouterr().out
    assert "GHOST" in out


def test_json_output_structure(env_file, parser, capsys):
    rc = _run(parser, env_file, ["--alias", "DB_HOST=database_host", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "aliased" in data
    assert "unaliased" in data
    assert "missing_keys" in data


def test_json_aliased_value_correct(env_file, parser, capsys):
    _run(parser, env_file, ["--alias", "DB_HOST=database_host", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["aliased"]["database_host"] == "localhost"


def test_dotenv_output_uses_alias_name(env_file, parser, capsys):
    _run(parser, env_file, ["--alias", "DB_PORT=port", "--format", "dotenv", "--no-unaliased"])
    out = capsys.readouterr().out
    assert "port=5432" in out
    assert "DB_PORT" not in out


def test_no_unaliased_flag_omits_extra_keys(env_file, parser, capsys):
    _run(parser, env_file, ["--alias", "DB_HOST=host", "--format", "json", "--no-unaliased"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["unaliased"] == {}


def test_strict_mode_returns_nonzero_on_missing(env_file, parser):
    rc = _run(parser, env_file, ["--alias", "NONEXISTENT=alias", "--strict"])
    assert rc == 1


def test_strict_mode_returns_zero_when_all_present(env_file, parser):
    rc = _run(parser, env_file, ["--alias", "DB_HOST=host", "--strict"])
    assert rc == 0


def test_no_aliases_returns_all_as_unaliased(env_file, parser, capsys):
    _run(parser, env_file, ["--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "DB_HOST" in data["unaliased"]
    assert data["aliased"] == {}
