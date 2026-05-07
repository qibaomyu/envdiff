"""Edge-case tests for envdiff.renamer."""

from envdiff.renamer import rename_keys


def test_rename_to_same_key():
    """Renaming A -> A is a no-op but should not crash."""
    env = {"A": "value"}
    result = rename_keys(env, {"A": "A"})
    assert result.env["A"] == "value"
    assert len(result.renamed()) == 1


def test_chain_rename_in_single_call():
    """A -> B and B -> C in one call: original B should survive unless keep_original=False."""
    env = {"A": "alpha", "B": "beta"}
    result = rename_keys(env, {"A": "B", "B": "C"}, overwrite=True)
    # B ends up as the value from A (overwrite), C gets original B
    assert result.env.get("C") == "beta"


def test_empty_value_is_renamed():
    env = {"EMPTY_KEY": ""}
    result = rename_keys(env, {"EMPTY_KEY": "NEW_EMPTY"})
    assert "NEW_EMPTY" in result.env
    assert result.env["NEW_EMPTY"] == ""


def test_rename_result_env_contains_untouched_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    result = rename_keys(env, {"A": "ALPHA"})
    assert "B" in result.env
    assert "C" in result.env


def test_rename_entry_repr_contains_arrow():
    from envdiff.renamer import RenameEntry
    entry = RenameEntry(old_key="OLD", new_key="NEW", value="v")
    assert "OLD" in repr(entry)
    assert "NEW" in repr(entry)


def test_multiple_skips_counted_in_summary():
    env = {"X": "1"}
    result = rename_keys(env, {"MISSING1": "A", "MISSING2": "B"})
    assert "2 skipped" in result.summary()
    assert "0 key(s) renamed" in result.summary()
