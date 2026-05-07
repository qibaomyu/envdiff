"""Mask environment variable values for safe display or logging."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_MASK = "***"
_PARTIAL_VISIBLE = 4  # number of trailing chars to reveal in partial mode


@dataclass
class MaskResult:
    original_key: str
    masked_value: str
    was_masked: bool

    def __repr__(self) -> str:  # pragma: no cover
        return f"MaskResult(key={self.original_key!r}, masked={self.was_masked})"


def mask_value(
    value: str,
    *,
    mask: str = DEFAULT_MASK,
    partial: bool = False,
) -> str:
    """Return a masked representation of *value*.

    If *partial* is True the last ``_PARTIAL_VISIBLE`` characters are kept so
    that values can be distinguished without exposing the full secret.
    """
    if not value:
        return value
    if partial and len(value) > _PARTIAL_VISIBLE:
        return mask + value[-_PARTIAL_VISIBLE:]
    return mask


def mask_env(
    env: Dict[str, str],
    keys: List[str],
    *,
    mask: str = DEFAULT_MASK,
    partial: bool = False,
) -> Dict[str, MaskResult]:
    """Return a dict mapping every key in *env* to a :class:`MaskResult`.

    Keys listed in *keys* have their values replaced; all others are kept as-is
    but still wrapped in ``MaskResult`` for uniform downstream handling.
    """
    result: Dict[str, MaskResult] = {}
    keys_set = set(keys)
    for k, v in env.items():
        if k in keys_set:
            result[k] = MaskResult(
                original_key=k,
                masked_value=mask_value(v, mask=mask, partial=partial),
                was_masked=True,
            )
        else:
            result[k] = MaskResult(original_key=k, masked_value=v, was_masked=False)
    return result


def mask_summary(results: Dict[str, MaskResult]) -> str:
    """Return a human-readable summary of masking activity."""
    total = len(results)
    masked = sum(1 for r in results.values() if r.was_masked)
    return f"{masked}/{total} keys masked."
