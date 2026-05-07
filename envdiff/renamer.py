"""Rename or alias environment variable keys across an env mapping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameEntry:
    old_key: str
    new_key: str
    value: str
    skipped: bool = False
    skip_reason: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        status = f"skipped({self.skip_reason})" if self.skipped else "renamed"
        return f"RenameEntry({self.old_key!r} -> {self.new_key!r}, {status})"


@dataclass
class RenameResult:
    entries: List[RenameEntry] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def renamed(self) -> List[RenameEntry]:
        return [e for e in self.entries if not e.skipped]

    def skipped(self) -> List[RenameEntry]:
        return [e for e in self.entries if e.skipped]

    def summary(self) -> str:
        r = len(self.renamed())
        s = len(self.skipped())
        return f"{r} key(s) renamed, {s} skipped"


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    *,
    overwrite: bool = False,
    keep_original: bool = False,
) -> RenameResult:
    """Rename keys in *env* according to *mapping* (old -> new).

    Parameters
    ----------
    env:          Source environment dict.
    mapping:      Dict of {old_key: new_key} rename rules.
    overwrite:    If False (default) skip renames where new_key already exists.
    keep_original: If True, retain the original key alongside the renamed one.
    """
    result_env: Dict[str, str] = dict(env)
    entries: List[RenameEntry] = []

    for old_key, new_key in mapping.items():
        if old_key not in env:
            entries.append(
                RenameEntry(old_key, new_key, "", skipped=True, skip_reason="key not found")
            )
            continue

        value = env[old_key]

        if new_key in result_env and not overwrite:
            entries.append(
                RenameEntry(old_key, new_key, value, skipped=True, skip_reason="target key exists")
            )
            continue

        result_env[new_key] = value
        if not keep_original:
            result_env.pop(old_key, None)
        entries.append(RenameEntry(old_key, new_key, value))

    return RenameResult(entries=entries, env=result_env)
