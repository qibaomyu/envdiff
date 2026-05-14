"""Tests for envdiff.archiver."""
import json
from pathlib import Path

import pytest

from envdiff.archiver import (
    EnvArchive,
    ArchiveEntry,
    _checksum,
    save_archive,
    load_archive,
    ARCHIVE_VERSION,
)


@pytest.fixture
def sample_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}


@pytest.fixture
def archive(sample_env):
    a = EnvArchive()
    a.add("production", sample_env)
    a.add("staging", {"DB_HOST": "staging-db", "DB_PORT": "5432"})
    return a


def test_archive_starts_empty():
    a = EnvArchive()
    assert a.entries == []


def test_add_entry_returns_archive_entry(sample_env):
    a = EnvArchive()
    entry = a.add("prod", sample_env)
    assert isinstance(entry, ArchiveEntry)
    assert entry.label == "prod"


def test_add_increments_entries(sample_env):
    a = EnvArchive()
    a.add("prod", sample_env)
    a.add("staging", sample_env)
    assert len(a.entries) == 2


def test_labels_returns_all_labels(archive):
    assert "production" in archive.labels()
    assert "staging" in archive.labels()


def test_get_returns_correct_entry(archive, sample_env):
    entry = archive.get("production")
    assert entry is not None
    assert entry.env == sample_env


def test_get_missing_label_returns_none(archive):
    assert archive.get("nonexistent") is None


def test_checksum_is_deterministic(sample_env):
    c1 = _checksum(sample_env)
    c2 = _checksum(sample_env)
    assert c1 == c2


def test_checksum_differs_for_different_envs(sample_env):
    other = {"DB_HOST": "other"}
    assert _checksum(sample_env) != _checksum(other)


def test_checksum_is_16_chars(sample_env):
    assert len(_checksum(sample_env)) == 16


def test_entry_has_checksum(sample_env):
    a = EnvArchive()
    entry = a.add("prod", sample_env)
    assert len(entry.checksum) == 16


def test_archive_version_set():
    a = EnvArchive()
    assert a.version == ARCHIVE_VERSION


def test_save_and_load_roundtrip(tmp_path, archive):
    p = tmp_path / "archive.json"
    save_archive(archive, p)
    loaded = load_archive(p)
    assert loaded.labels() == archive.labels()
    assert loaded.get("production").env == archive.get("production").env


def test_save_creates_file(tmp_path, archive):
    p = tmp_path / "archive.json"
    save_archive(archive, p)
    assert p.exists()


def test_load_preserves_version(tmp_path, archive):
    p = tmp_path / "archive.json"
    save_archive(archive, p)
    loaded = load_archive(p)
    assert loaded.version == ARCHIVE_VERSION


def test_load_returns_string_values(tmp_path):
    a = EnvArchive()
    a.add("env", {"PORT": "8080"})
    p = tmp_path / "archive.json"
    save_archive(a, p)
    loaded = load_archive(p)
    entry = loaded.get("env")
    assert isinstance(entry.env["PORT"], str)


def test_load_missing_file_raises(tmp_path):
    """Loading a non-existent archive file should raise FileNotFoundError."""
    p = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_archive(p)


def test_load_invalid_json_raises(tmp_path):
    """Loading a file with invalid JSON should raise a ValueError."""
    p = tmp_path / "bad_archive.json"
    p.write_text("not valid json {{{")
    with pytest.raises((ValueError, json.JSONDecodeError)):
        load_archive(p)
