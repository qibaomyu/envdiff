"""Tests for envdiff.sorter and envdiff.cli_sort."""

from __future__ import annotations

import argparse
import io
import json
import textwrap
from pathlib import Path

import pytest

from envdiff.sorter import SortBy, SortOrder, SortedEnv, rank_by_value_length, sort_env
from envdiff.cli_sort import add_sort_args, run_sort


@pytest.fixture
def sample_env() -> dict:
    return {
        "ZEBRA": "last",
        "APPLE": "first",
        "MANGO": "middle",
        "DB_URL": "postgresql://localhost/db",
        "SHORT": "x",
    }


# --- sorter unit tests ---

def test_sort_by_key_asc(sample_env):
    result = sort_env(sample_env, sort_by=SortBy.KEY, order=SortOrder.ASC)
    assert result.keys() == ["APPLE", "DB_URL", "MANGO", "SHORT", "ZEBRA"]


def test_sort_by_key_desc(sample_env):
    result = sort_env(sample_env, sort_by=SortBy.KEY, order=SortOrder.DESC)
    assert result.keys()[0] == "ZEBRA"


def test_sort_by_value_length_asc(sample_env):
    result = sort_env(sample_env, sort_by=SortBy.VALUE_LENGTH, order=SortOrder.ASC)
    assert result.keys()[0] == "SHORT"  # value "x" is shortest


def test_sort_by_value_length_desc(sample_env):
    result = sort_env(sample_env, sort_by=SortBy.VALUE_LENGTH, order=SortOrder.DESC)
    assert result.keys()[0] == "DB_URL"  # longest value


def test_sort_by_value_asc(sample_env):
    result = sort_env(sample_env, sort_by=SortBy.VALUE, order=SortOrder.ASC)
    assert result.keys()[0] == "APPLE"  # value "first"


def test_sorted_env_as_dict(sample_env):
    result = sort_env(sample_env)
    d = result.as_dict()
    assert isinstance(d, dict)
    assert set(d.keys()) == set(sample_env.keys())


def test_sorted_env_len(sample_env):
    result = sort_env(sample_env)
    assert len(result) == len(sample_env)


def test_rank_by_value_length_top2(sample_env):
    top = rank_by_value_length(sample_env, top_n=2)
    assert len(top) == 2
    assert top[0][0] == "DB_URL"


def test_rank_by_value_length_exceeds_size(sample_env):
    top = rank_by_value_length(sample_env, top_n=100)
    assert len(top) == len(sample_env)


# --- cli_sort integration tests ---

@pytest.fixture
def env_file(tmp_path) -> Path:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent("""\
        ZEBRA=last
        APPLE=first
        MANGO=middle
    """))
    return p


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_sort_args(sub)
    return p


def _run(parser, argv, **kwargs):
    args = parser.parse_args(argv)
    out = io.StringIO()
    err = io.StringIO()
    code = args.func(args, out=out, err=err)
    return code, out.getvalue(), err.getvalue()


def test_sort_text_output_default(env_file, parser):
    code, out, _ = _run(parser, ["sort", str(env_file)])
    assert code == 0
    lines = out.strip().splitlines()
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys)


def test_sort_json_output(env_file, parser):
    code, out, _ = _run(parser, ["sort", str(env_file), "--format", "json"])
    assert code == 0
    data = json.loads(out)
    assert "APPLE" in data


def test_sort_top_n(env_file, parser):
    code, out, _ = _run(parser, ["sort", str(env_file), "--top", "2"])
    assert code == 0
    assert len(out.strip().splitlines()) == 2


def test_sort_missing_file(parser):
    code, _, err = _run(parser, ["sort", "/nonexistent/.env"])
    assert code == 1
    assert "not found" in err
