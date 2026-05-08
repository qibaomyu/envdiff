"""Flatten nested structures (e.g. JSON values) within an env dict into
dot-separated keys, and restore them back."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenEntry:
    original_key: str
    flat_key: str
    value: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"FlattenEntry({self.original_key!r} -> {self.flat_key!r})"


@dataclass
class FlattenResult:
    entries: List[FlattenEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def as_env(self) -> Dict[str, str]:
        """Return the flattened key/value pairs as a plain dict."""
        return {e.flat_key: e.value for e in self.entries}

    def summary(self) -> str:
        return (
            f"Flattened {len(self.entries)} key(s); "
            f"{len(self.skipped)} skipped (non-JSON)."
        )


def _flatten_dict(
    obj: dict,
    prefix: str = "",
    separator: str = ".",
) -> Dict[str, str]:
    """Recursively flatten *obj* into dot-separated string keys."""
    result: Dict[str, str] = {}
    for k, v in obj.items():
        new_key = f"{prefix}{separator}{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten_dict(v, new_key, separator))
        else:
            result[new_key] = str(v) if not isinstance(v, str) else v
    return result


def flatten_env(
    env: Dict[str, str],
    separator: str = ".",
    only_json_values: bool = True,
) -> FlattenResult:
    """Flatten every value that is a JSON object into separate keys.

    Parameters
    ----------
    env:
        Source environment dict.
    separator:
        Character(s) used to join nested key segments.
    only_json_values:
        When *True* (default) only values that parse as a JSON *object*
        are expanded; all others are kept as-is.
    """
    result = FlattenResult()
    for key, value in env.items():
        parsed: Optional[dict] = None
        try:
            candidate = json.loads(value)
            if isinstance(candidate, dict):
                parsed = candidate
        except (json.JSONDecodeError, TypeError):
            pass

        if parsed is not None:
            flat = _flatten_dict(parsed, prefix=key, separator=separator)
            for flat_key, flat_val in flat.items():
                result.entries.append(FlattenEntry(key, flat_key, flat_val))
        else:
            # Keep the original key unchanged.
            result.entries.append(FlattenEntry(key, key, value))
            if only_json_values is False:
                pass  # already appended above
            else:
                result.skipped.append(key)

    return result
