"""Tests for envdiff.cli_archive."""
import argparse
import json
from pathlib import Path

import pytest

from envdiff.cli_archive import add_archive_args, run_archive
from envdiff.archiver import EnvArchive, save_archive


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "prod.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n")
    return p


@pytest.fixture
def archive_file(tmp_path):
    return tmp_path / "bundle.json"


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_archive_args(sub)
    return p


def _run(parser, argv):
    args = parser.parse_args(argv)
    return run_archive(args)


def test_add_creates_archive(parser, env_file, archive_file):
    rc = _run(parser, ["archive", "add", str(archive_file), str(env_file), "--label", "prod"])
    assert rc == 0
    assert archive_file.exists()


def test_add_stores_label(parser, env_file, archive_file):
    _run(parser, ["archive", "add", str(archive_file), str(env_file), "--label", "prod"])
    data = json.loads(archive_file.read_text())
    labels = [e["label"] for e in data["entries"]]
    assert "prod" in labels


def test_add_twice_appends(parser, env_file, archive_file):
    _run(parser, ["archive", "add", str(archive_file), str(env_file), "--label", "prod"])
    _run(parser, ["archive", "add", str(archive_file), str(env_file), "--label", "staging"])
    data = json.loads(archive_file.read_text())
    assert len(data["entries"]) == 2


def test_list_text_output(parser, env_file, archive_file, capsys):
    _run(parser, ["archive", "add", str(archive_file), str(env_file), "--label", "prod"])
    rc = _run(parser, ["archive", "list", str(archive_file)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "prod" in captured.out


def test_list_json_output(parser, env_file, archive_file, capsys):
    _run(parser, ["archive", "add", str(archive_file), str(env_file), "--label", "prod"])
    _run(parser, ["archive", "list", str(archive_file), "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["label"] == "prod"


def test_show_text_output(parser, env_file, archive_file, capsys):
    _run(parser, ["archive", "add", str(archive_file), str(env_file), "--label", "prod"])
    rc = _run(parser, ["archive", "show", str(archive_file), "prod"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "DB_HOST" in captured.out


def test_show_json_output(parser, env_file, archive_file, capsys):
    _run(parser, ["archive", "add", str(archive_file), str(env_file), "--label", "prod"])
    _run(parser, ["archive", "show", str(archive_file), "prod", "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["label"] == "prod"
    assert "DB_HOST" in data["env"]


def test_show_missing_label_returns_nonzero(parser, env_file, archive_file):
    _run(parser, ["archive", "add", str(archive_file), str(env_file), "--label", "prod"])
    rc = _run(parser, ["archive", "show", str(archive_file), "ghost"])
    assert rc == 1


def test_list_empty_archive(parser, tmp_path, capsys):
    a = EnvArchive()
    p = tmp_path / "empty.json"
    save_archive(a, p)
    rc = _run(parser, ["archive", "list", str(p)])
    assert rc == 0
    assert "(no entries)" in capsys.readouterr().out
