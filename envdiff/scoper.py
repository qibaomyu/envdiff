"""Scoper: restrict or project an env dict to a named scope (prefix-based namespace)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    """Result of scoping an environment dictionary."""

    scope: str
    stripped: Dict[str, str] = field(default_factory=dict)
    original_keys: Dict[str, str] = field(default_factory=dict)  # stripped_key -> original_key

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScopeResult(scope={self.scope!r}, keys={list(self.stripped)})"

    def __len__(self) -> int:
        return len(self.stripped)

    def restore(self) -> Dict[str, str]:
        """Return the scoped values with their original prefixed keys restored."""
        return {self.original_keys[k]: v for k, v in self.stripped.items()}


def scope_env(
    env: Dict[str, str],
    scope: str,
    separator: str = "_",
    strip_prefix: bool = True,
) -> ScopeResult:
    """Extract keys that belong to *scope* (i.e. start with ``scope + separator``).

    Args:
        env: Source environment dictionary.
        scope: The prefix/namespace to filter on (case-insensitive comparison).
        separator: Character that separates the scope from the rest of the key.
        strip_prefix: When *True* the scope prefix is removed from the returned keys.

    Returns:
        A :class:`ScopeResult` containing only the matching keys.
    """
    prefix = scope.upper() + separator
    stripped: Dict[str, str] = {}
    original_keys: Dict[str, str] = {}

    for key, value in env.items():
        if key.upper().startswith(prefix):
            if strip_prefix:
                short = key[len(prefix):]
            else:
                short = key
            stripped[short] = value
            original_keys[short] = key

    return ScopeResult(scope=scope.upper(), stripped=stripped, original_keys=original_keys)


def list_scopes(
    env: Dict[str, str],
    separator: str = "_",
    min_keys: int = 1,
) -> List[str]:
    """Discover all distinct scope prefixes present in *env*.

    A scope is the portion of a key before the first *separator*.
    Only scopes that have at least *min_keys* keys are returned.

    Returns:
        Sorted list of scope strings (upper-case).
    """
    from collections import Counter

    counts: Counter = Counter()
    for key in env:
        if separator in key:
            prefix = key.split(separator, 1)[0].upper()
            counts[prefix] += 1

    return sorted(scope for scope, count in counts.items() if count >= min_keys)
