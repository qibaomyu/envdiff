"""Normalizes environment variable keys and values for consistent comparison."""

from __future__ import annotations

import re
from typing import Dict, Optional


Normalized = Dict[str, str]


def normalize_key(key: str, *, uppercase: bool = True, strip: bool = True) -> str:
    """Normalize a single environment variable key.

    Args:
        key: The raw key string.
        uppercase: Convert key to uppercase when True (default).
        strip: Strip surrounding whitespace when True (default).

    Returns:
        The normalized key string.
    """
    if strip:
        key = key.strip()
    if uppercase:
        key = key.upper()
    return key


def normalize_value(
    value: str,
    *,
    strip: bool = True,
    collapse_whitespace: bool = False,
    remove_quotes: bool = True,
) -> str:
    """Normalize a single environment variable value.

    Args:
        value: The raw value string.
        strip: Strip surrounding whitespace when True (default).
        collapse_whitespace: Replace internal runs of whitespace with a single
            space when True.
        remove_quotes: Remove surrounding single or double quotes when True
            (default).

    Returns:
        The normalized value string.
    """
    if strip:
        value = value.strip()
    if remove_quotes and len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
    if collapse_whitespace:
        value = re.sub(r'\s+', ' ', value)
    return value


def normalize_env(
    env: Dict[str, str],
    *,
    uppercase_keys: bool = True,
    strip_keys: bool = True,
    strip_values: bool = True,
    collapse_whitespace: bool = False,
    remove_quotes: bool = True,
) -> Normalized:
    """Return a new dict with all keys and values normalized.

    Duplicate keys that result from normalization (e.g. 'foo' and 'FOO') are
    resolved by keeping the last value encountered during iteration.
    """
    result: Normalized = {}
    for raw_key, raw_value in env.items():
        norm_key = normalize_key(raw_key, uppercase=uppercase_keys, strip=strip_keys)
        norm_value = normalize_value(
            raw_value,
            strip=strip_values,
            collapse_whitespace=collapse_whitespace,
            remove_quotes=remove_quotes,
        )
        result[norm_key] = norm_value
    return result
