"""Filter utilities for environment variable comparisons."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional


def filter_keys(
    env: Dict[str, str],
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a copy of *env* keeping only keys that match the filter rules.

    Rules are evaluated in order:
    1. If *include_patterns* is provided, only keys matching at least one
       pattern are kept.
    2. Keys matching any *exclude_patterns* pattern are then removed.

    Patterns follow Unix shell-style wildcards (``fnmatch``).
    """
    result = dict(env)

    if include_patterns:
        result = {
            k: v
            for k, v in result.items()
            if any(fnmatch.fnmatch(k, p) for p in include_patterns)
        }

    if exclude_patterns:
        result = {
            k: v
            for k, v in result.items()
            if not any(fnmatch.fnmatch(k, p) for p in exclude_patterns)
        }

    return result


def filter_keys_by_prefix(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return only the keys that start with *prefix* (case-sensitive)."""
    return {k: v for k, v in env.items() if k.startswith(prefix)}


def filter_keys_by_regex(
    env: Dict[str, str],
    pattern: str,
    exclude: bool = False,
) -> Dict[str, str]:
    """Filter keys using a regular expression.

    When *exclude* is ``True`` the matching keys are removed instead of kept.
    """
    compiled = re.compile(pattern)
    if exclude:
        return {k: v for k, v in env.items() if not compiled.search(k)}
    return {k: v for k, v in env.items() if compiled.search(k)}
