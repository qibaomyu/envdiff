"""Detect and report duplicate values across environment variable keys."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DuplicateGroup:
    """A set of keys that share the same value."""

    value: str
    keys: List[str]

    def __repr__(self) -> str:  # pragma: no cover
        return f"DuplicateGroup(value={self.value!r}, keys={self.keys})"

    def __len__(self) -> int:
        return len(self.keys)


@dataclass
class DeduplicationResult:
    """Result of a deduplication scan over an env mapping."""

    groups: List[DuplicateGroup] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.groups) > 0

    @property
    def total_duplicate_keys(self) -> int:
        """Number of keys involved in at least one duplicate group."""
        return sum(len(g) for g in self.groups)

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate values found."
        lines = [f"{len(self.groups)} duplicate value group(s) found:"]
        for g in self.groups:
            keys_str = ", ".join(sorted(g.keys))
            lines.append(f"  value={g.value!r} -> [{keys_str}]")
        return "\n".join(lines)


def find_duplicates(
    env: Dict[str, str],
    ignore_empty: bool = True,
    ignore_keys: Optional[List[str]] = None,
) -> DeduplicationResult:
    """Scan *env* and return keys that share identical values.

    Parameters
    ----------
    env:
        Mapping of environment variable names to their values.
    ignore_empty:
        When *True* (default) empty-string values are not considered duplicates.
    ignore_keys:
        Optional list of key names to exclude from the scan.
    """
    ignore_keys = set(ignore_keys or [])
    value_map: Dict[str, List[str]] = defaultdict(list)

    for key, value in env.items():
        if key in ignore_keys:
            continue
        if ignore_empty and value == "":
            continue
        value_map[value].append(key)

    groups = [
        DuplicateGroup(value=val, keys=keys)
        for val, keys in value_map.items()
        if len(keys) > 1
    ]
    # stable, deterministic ordering
    groups.sort(key=lambda g: sorted(g.keys)[0])
    return DeduplicationResult(groups=groups)
