"""Aliaser: map environment variable keys to human-friendly aliases."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasEntry:
    original_key: str
    alias: str
    value: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"AliasEntry({self.original_key!r} -> {self.alias!r})"


@dataclass
class AliasResult:
    entries: List[AliasEntry] = field(default_factory=list)
    unaliased: Dict[str, str] = field(default_factory=dict)

    # keys that were requested but not present in the env
    missing_keys: List[str] = field(default_factory=list)

    def by_alias(self) -> Dict[str, str]:
        """Return a dict keyed by alias name."""
        return {e.alias: e.value for e in self.entries}

    def by_original(self) -> Dict[str, str]:
        """Return a dict keyed by original key name."""
        return {e.original_key: e.value for e in self.entries}

    def summary(self) -> str:
        lines = [f"Aliased: {len(self.entries)}, Unaliased: {len(self.unaliased)}, Missing: {len(self.missing_keys)}"]
        for e in self.entries:
            lines.append(f"  {e.original_key} -> {e.alias}")
        if self.missing_keys:
            lines.append("Missing keys:")
            for k in self.missing_keys:
                lines.append(f"  {k}")
        return "\n".join(lines)


def alias_env(
    env: Dict[str, str],
    aliases: Dict[str, str],
    include_unaliased: bool = True,
) -> AliasResult:
    """Apply *aliases* (original_key -> alias) to *env*.

    Parameters
    ----------
    env:
        The source environment mapping.
    aliases:
        A dict mapping original key names to desired alias names.
    include_unaliased:
        When True, keys not covered by *aliases* are kept in
        ``AliasResult.unaliased``.
    """
    entries: List[AliasEntry] = []
    missing: List[str] = []

    for original, alias in aliases.items():
        if original in env:
            entries.append(AliasEntry(original_key=original, alias=alias, value=env[original]))
        else:
            missing.append(original)

    aliased_originals = {e.original_key for e in entries}
    unaliased: Dict[str, str] = {}
    if include_unaliased:
        unaliased = {k: v for k, v in env.items() if k not in aliased_originals}

    return AliasResult(entries=entries, unaliased=unaliased, missing_keys=missing)
