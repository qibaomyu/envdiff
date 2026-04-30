"""Tests for envdiff.loader module."""

import os
import pytest
from pathlib import Path

from envdiff.loader import load_env_file, load_from_os_environ


@pytest.fixture
def sample_env_file(tmp_path: Path) -> Path:
    content = """
# Database config
DB_HOST=localhost
DB_PORT=5432
DB_NAME="mydb"
SECRET_KEY='supersecret'

DEBUG=true
"""
    env_file = tmp_path / ".env"
    env_file.write_text(content)
    return env_file


def test_load_env_file_basic(sample_env_file):
    result = load_env_file(sample_env_file)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["DB_NAME"] == "mydb"
    assert result["SECRET_KEY"] == "supersecret"
    assert result["DEBUG"] == "true"


def test_load_env_file_ignores_comments_and_blanks(sample_env_file):
    result = load_env_file(sample_env_file)
    assert len(result) == 5


def test_load_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_env_file("/nonexistent/path/.env")


def test_load_env_file_invalid_line(tmp_path):
    bad_file = tmp_path / ".env"
    bad_file.write_text("INVALID_LINE_NO_EQUALS\n")
    with pytest.raises(ValueError, match="Invalid format"):
        load_env_file(bad_file)


def test_load_env_file_empty_key(tmp_path):
    bad_file = tmp_path / ".env"
    bad_file.write_text("=value\n")
    with pytest.raises(ValueError, match="Empty key"):
        load_env_file(bad_file)


def test_load_from_os_environ_no_prefix(monkeypatch):
    monkeypatch.setenv("TEST_VAR_XYZ", "hello")
    result = load_from_os_environ()
    assert "TEST_VAR_XYZ" in result
    assert result["TEST_VAR_XYZ"] == "hello"


def test_load_from_os_environ_with_prefix(monkeypatch):
    monkeypatch.setenv("MYAPP_HOST", "prod.example.com")
    monkeypatch.setenv("OTHER_VAR", "ignored")
    result = load_from_os_environ(prefix="MYAPP_")
    assert "MYAPP_HOST" in result
    assert "OTHER_VAR" not in result
