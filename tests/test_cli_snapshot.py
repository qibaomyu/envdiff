"""Tests for envdiff.cli_snapshot."""

import argparse
import json
import os
import pytest

from envdiff.cli_snapshot import add_snapshot_args, run_snapshot
from envdiff.snapshot import load_snapshot, snapshot_metadata


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "test.env"
    p.write_text("APP_ENV=staging\nDB_PORT=5432\n")
    return str(p)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_snapshot_args(sub)
    return p


def test_save_creates_snapshot(parser, env_file, tmp_path):
    out = str(tmp_path / "snap.json")
    args = parser.parse_args(["snapshot", "save", env_file, out])
    code = run_snapshot(args)
    assert code == 0
    assert os.path.exists(out)


def test_save_snapshot_roundtrip(parser, env_file, tmp_path):
    out = str(tmp_path / "snap.json")
    args = parser.parse_args(["snapshot", "save", env_file, out])
    run_snapshot(args)
    loaded = load_snapshot(out)
    assert loaded["APP_ENV"] == "staging"
    assert loaded["DB_PORT"] == "5432"


def test_save_with_label(parser, env_file, tmp_path):
    out = str(tmp_path / "snap.json")
    args = parser.parse_args(["snapshot", "save", env_file, out, "--label", "my-label"])
    run_snapshot(args)
    meta = snapshot_metadata(out)
    assert meta["label"] == "my-label"


def test_save_with_metadata(parser, env_file, tmp_path):
    out = str(tmp_path / "snap.json")
    args = parser.parse_args(
        ["snapshot", "save", env_file, out, "--meta", "region=eu-west-1", "team=backend"]
    )
    run_snapshot(args)
    meta = snapshot_metadata(out)
    assert meta["metadata"]["region"] == "eu-west-1"
    assert meta["metadata"]["team"] == "backend"


def test_inspect_outputs_json(parser, env_file, tmp_path, capsys):
    out = str(tmp_path / "snap.json")
    save_args = parser.parse_args(["snapshot", "save", env_file, out])
    run_snapshot(save_args)

    inspect_args = parser.parse_args(["snapshot", "inspect", out])
    code = run_snapshot(inspect_args)
    assert code == 0
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert data["key_count"] == 2
    assert "captured_at" in data


def test_save_from_os_environ(parser, tmp_path, monkeypatch):
    monkeypatch.setenv("_TEST_SNAP_KEY", "hello")
    out = str(tmp_path / "environ.json")
    # No env_file argument → reads os.environ
    args = parser.parse_args(["snapshot", "save", out])
    code = run_snapshot(args)
    assert code == 0
    loaded = load_snapshot(out)
    assert loaded.get("_TEST_SNAP_KEY") == "hello"
