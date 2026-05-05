"""Tests for envdiff.snapshot."""

import json
import os
import pytest

from envdiff.snapshot import save_snapshot, load_snapshot, snapshot_metadata, SNAPSHOT_VERSION


SAMPLE_ENV = {"APP_ENV": "production", "DB_HOST": "db.example.com", "PORT": "5432"}


@pytest.fixture
def snapshot_file(tmp_path):
    p = tmp_path / "snap.json"
    save_snapshot(SAMPLE_ENV, str(p), label="prod")
    return str(p)


def test_save_creates_file(tmp_path):
    p = tmp_path / "env.snap.json"
    save_snapshot(SAMPLE_ENV, str(p))
    assert p.exists()


def test_save_contains_correct_version(tmp_path):
    p = tmp_path / "snap.json"
    save_snapshot(SAMPLE_ENV, str(p))
    data = json.loads(p.read_text())
    assert data["version"] == SNAPSHOT_VERSION


def test_save_and_load_roundtrip(snapshot_file):
    loaded = load_snapshot(snapshot_file)
    assert loaded == SAMPLE_ENV


def test_load_returns_string_values(tmp_path):
    p = tmp_path / "snap.json"
    # Store numeric-looking values
    save_snapshot({"NUM": "42", "FLAG": "true"}, str(p))
    loaded = load_snapshot(str(p))
    assert all(isinstance(v, str) for v in loaded.values())


def test_load_unsupported_version(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"version": 99, "env": {}}))
    with pytest.raises(ValueError, match="Unsupported snapshot version"):
        load_snapshot(str(p))


def test_load_missing_env_key(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"version": SNAPSHOT_VERSION}))
    with pytest.raises(ValueError, match="missing a valid 'env' mapping"):
        load_snapshot(str(p))


def test_load_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_snapshot("/nonexistent/path/snap.json")


def test_snapshot_metadata_label(snapshot_file):
    meta = snapshot_metadata(snapshot_file)
    assert meta["label"] == "prod"


def test_snapshot_metadata_has_captured_at(snapshot_file):
    meta = snapshot_metadata(snapshot_file)
    assert meta["captured_at"] is not None
    assert "T" in meta["captured_at"]  # ISO format


def test_snapshot_metadata_custom(tmp_path):
    p = tmp_path / "snap.json"
    save_snapshot(SAMPLE_ENV, str(p), metadata={"region": "us-east-1"})
    meta = snapshot_metadata(str(p))
    assert meta["metadata"]["region"] == "us-east-1"


def test_default_label_from_filename(tmp_path):
    p = tmp_path / "staging.json"
    save_snapshot(SAMPLE_ENV, str(p))
    meta = snapshot_metadata(str(p))
    assert meta["label"] == "staging"
