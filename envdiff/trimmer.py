"""Trim environment variables by removing keys with empty, whitespace-only,
or placeholder values from an env dict."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Common placeholder patterns that indicate a value is not really set
_PLACEHOLDER_PATTERNS: List[str] = [
    r"^<.*>$",          # <REPLACE_ME>, <your-value>
    r"^\$\{.*\}$",     # ${VAR_NAME}
    r"^%.*%$",          # %VAR_NAME%
    r"^CHANGE_ME$",
    r"^REPLACE_ME$",
    r"^TODO$",
    r"^FIXME$",
    r"^N/A$",
    r"^none$",
    r"^null$",
    r"^undefined$",
]


@dataclass
class TrimEntry:
    key: str
    value: str
    reason: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"TrimEntry(key={self.key!r}, reason={self.reason!r})"


@dataclass
class TrimResult:
    original: Dict[str, str]
    trimmed: Dict[str, str] = field(default_factory=dict)
    removed: List[TrimEntry] = field(default_factory=list)

    def has_removals(self) -> bool:
        return len(self.removed) > 0

    def summary(self) -> str:
        total = len(self.original)
        kept = len(self.trimmed)
        dropped = len(self.removed)
        return f"{kept}/{total} keys kept, {dropped} removed"


def _compile_placeholders(extra: Optional[List[str]] = None) -> List[re.Pattern]:
    patterns = list(_PLACEHOLDER_PATTERNS)
    if extra:
        patterns.extend(extra)
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def _is_placeholder(value: str, compiled: List[re.Pattern]) -> bool:
    return any(p.match(value) for p in compiled)


def trim_env(
    env: Dict[str, str],
    remove_empty: bool = True,
    remove_whitespace_only: bool = True,
    remove_placeholders: bool = True,
    extra_placeholder_patterns: Optional[List[str]] = None,
) -> TrimResult:
    """Return a TrimResult with keys removed according to the specified rules."""
    compiled = _compile_placeholders(extra_placeholder_patterns) if remove_placeholders else []
    trimmed: Dict[str, str] = {}
    removed: List[TrimEntry] = []

    for key, value in env.items():
        if remove_empty and value == "":
            removed.append(TrimEntry(key=key, value=value, reason="empty"))
        elif remove_whitespace_only and value.strip() == "" and value != "":
            removed.append(TrimEntry(key=key, value=value, reason="whitespace-only"))
        elif remove_placeholders and _is_placeholder(value.strip(), compiled):
            removed.append(TrimEntry(key=key, value=value, reason="placeholder"))
        else:
            trimmed[key] = value

    return TrimResult(original=dict(env), trimmed=trimmed, removed=removed)
