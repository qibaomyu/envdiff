"""Tests for envdiff.patcher."""
import pytest

from envdiff.patcher import (
    PatchInstruction,
    PatchResult,
    apply_patch,
)


@pytest.fixture
def base_env():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


# --- set ---

def test_set_adds_new_key(base_env):
    result = apply_patch(base_env, [PatchInstruction(op="set", key="NEW", value="val")])
    assert result.env["NEW"] == "val"


def test_set_overwrites_existing_key(base_env):
    result = apply_patch(base_env, [PatchInstruction(op="set", key="PORT", value="9999")])
    assert result.env["PORT"] == "9999"


def test_set_skipped_when_overwrite_disallowed(base_env):
    instr = PatchInstruction(op="set", key="PORT", value="9999")
    result = apply_patch(base_env, [instr], allow_overwrite=False)
    assert result.env["PORT"] == "5432"
    assert instr in result.skipped


def test_set_new_key_allowed_even_without_overwrite(base_env):
    instr = PatchInstruction(op="set", key="BRAND_NEW", value="x")
    result = apply_patch(base_env, [instr], allow_overwrite=False)
    assert result.env["BRAND_NEW"] == "x"
    assert instr in result.applied


# --- unset ---

def test_unset_removes_existing_key(base_env):
    result = apply_patch(base_env, [PatchInstruction(op="unset", key="DEBUG")])
    assert "DEBUG" not in result.env


def test_unset_missing_key_is_skipped(base_env):
    instr = PatchInstruction(op="unset", key="MISSING")
    result = apply_patch(base_env, [instr])
    assert instr in result.skipped


# --- rename ---

def test_rename_moves_key(base_env):
    result = apply_patch(
        base_env,
        [PatchInstruction(op="rename", key="HOST", new_key="DB_HOST")],
    )
    assert "HOST" not in result.env
    assert result.env["DB_HOST"] == "localhost"


def test_rename_missing_source_is_skipped(base_env):
    instr = PatchInstruction(op="rename", key="GHOST", new_key="SPIRIT")
    result = apply_patch(base_env, [instr])
    assert instr in result.skipped


def test_rename_without_new_key_is_skipped(base_env):
    instr = PatchInstruction(op="rename", key="HOST", new_key=None)
    result = apply_patch(base_env, [instr])
    assert instr in result.skipped


# --- ordering & summary ---

def test_instructions_applied_in_order(base_env):
    instrs = [
        PatchInstruction(op="set", key="PORT", value="6000"),
        PatchInstruction(op="set", key="PORT", value="7000"),
    ]
    result = apply_patch(base_env, instrs)
    assert result.env["PORT"] == "7000"


def test_summary_counts(base_env):
    instrs = [
        PatchInstruction(op="set", key="NEW", value="v"),
        PatchInstruction(op="unset", key="MISSING"),
    ]
    result = apply_patch(base_env, instrs)
    assert result.summary() == "1 applied, 1 skipped"


def test_original_env_not_mutated(base_env):
    original = dict(base_env)
    apply_patch(base_env, [PatchInstruction(op="unset", key="HOST")])
    assert base_env == original
