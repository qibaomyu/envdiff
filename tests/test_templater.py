"""Tests for envdiff.templater."""

from __future__ import annotations

import pytest

from envdiff.templater import (
    TemplateRenderError,
    find_placeholders,
    render_template,
    render_template_file,
)


# ---------------------------------------------------------------------------
# find_placeholders
# ---------------------------------------------------------------------------

def test_find_placeholders_single():
    assert find_placeholders("Hello {{ NAME }}") == ["NAME"]


def test_find_placeholders_multiple():
    result = find_placeholders("{{ HOST }}:{{ PORT }}/{{ DB }}")
    assert result == ["HOST", "PORT", "DB"]


def test_find_placeholders_deduplicates():
    result = find_placeholders("{{ X }} and {{ X }} again")
    assert result == ["X"]


def test_find_placeholders_none():
    assert find_placeholders("no placeholders here") == []


def test_find_placeholders_extra_whitespace():
    assert find_placeholders("{{  KEY  }}") == ["KEY"]


# ---------------------------------------------------------------------------
# render_template — strict mode (default)
# ---------------------------------------------------------------------------

def test_render_simple_substitution():
    result = render_template("Hello {{ NAME }}", {"NAME": "world"})
    assert result == "Hello world"


def test_render_multiple_keys():
    tmpl = "{{ HOST }}:{{ PORT }}"
    result = render_template(tmpl, {"HOST": "localhost", "PORT": "5432"})
    assert result == "localhost:5432"


def test_render_missing_key_raises_in_strict_mode():
    with pytest.raises(TemplateRenderError) as exc_info:
        render_template("{{ MISSING }}", {})
    assert exc_info.value.key == "MISSING"


def test_render_error_message_contains_key():
    with pytest.raises(TemplateRenderError, match="MISSING"):
        render_template("{{ MISSING }}", {})


def test_render_no_placeholders_returns_unchanged():
    tmpl = "plain text"
    assert render_template(tmpl, {}) == tmpl


# ---------------------------------------------------------------------------
# render_template — non-strict mode
# ---------------------------------------------------------------------------

def test_render_missing_key_uses_default_when_not_strict():
    result = render_template("{{ MISSING }}", {}, strict=False, default="N/A")
    assert result == "N/A"


def test_render_missing_key_keeps_placeholder_when_no_default():
    result = render_template("{{ MISSING }}", {}, strict=False)
    assert result == "{{ MISSING }}"


def test_render_partial_substitution_non_strict():
    result = render_template(
        "{{ PRESENT }} and {{ ABSENT }}",
        {"PRESENT": "yes"},
        strict=False,
        default="?",
    )
    assert result == "yes and ?"


# ---------------------------------------------------------------------------
# render_template_file
# ---------------------------------------------------------------------------

def test_render_template_file(tmp_path):
    tmpl_file = tmp_path / "config.tmpl"
    tmpl_file.write_text("DB_URL={{ DB_HOST }}:{{ DB_PORT }}/mydb")
    result = render_template_file(
        str(tmpl_file), {"DB_HOST": "db.example.com", "DB_PORT": "5432"}
    )
    assert result == "DB_URL=db.example.com:5432/mydb"


def test_render_template_file_not_found():
    with pytest.raises(FileNotFoundError):
        render_template_file("/nonexistent/path/template.tmpl", {})
