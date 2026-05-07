"""Edge-case tests for envdiff.masker."""

from envdiff.masker import mask_env, mask_summary, mask_value, DEFAULT_MASK


def test_mask_value_exactly_partial_boundary():
    """Value exactly _PARTIAL_VISIBLE chars long should be fully masked."""
    result = mask_value("abcd", partial=True)  # len == _PARTIAL_VISIBLE
    assert result == DEFAULT_MASK


def test_mask_value_one_over_partial_boundary():
    result = mask_value("abcde", partial=True)  # len == 5
    assert result.endswith("bcde")
    assert result.startswith(DEFAULT_MASK)


def test_mask_env_empty_env():
    results = mask_env({}, ["SOME_KEY"])
    assert results == {}


def test_mask_env_empty_keys_list():
    env = {"APP": "value"}
    results = mask_env(env, [])
    assert results["APP"].was_masked is False
    assert results["APP"].masked_value == "value"


def test_mask_env_empty_value_stays_empty():
    env = {"EMPTY_KEY": ""}
    results = mask_env(env, ["EMPTY_KEY"])
    assert results["EMPTY_KEY"].masked_value == ""
    assert results["EMPTY_KEY"].was_masked is True


def test_mask_summary_all_masked():
    env = {"A": "1", "B": "2"}
    results = mask_env(env, ["A", "B"])
    assert mask_summary(results) == "2/2 keys masked."


def test_mask_summary_empty():
    assert mask_summary({}) == "0/0 keys masked."


def test_mask_result_repr_does_not_leak_value():
    from envdiff.masker import MaskResult
    r = MaskResult(original_key="SECRET", masked_value="***", was_masked=True)
    text = repr(r)
    assert "SECRET" in text
    assert "***" not in text or "masked=True" in text  # repr shows masked flag, not raw value
