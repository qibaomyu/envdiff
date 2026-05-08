"""Split a flat env dict into multiple named buckets based on rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SplitBucket:
    name: str
    env: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return f"SplitBucket(name={self.name!r}, keys={list(self.env.keys())})"

    def __len__(self) -> int:
        return len(self.env)


@dataclass
class SplitResult:
    buckets: Dict[str, SplitBucket] = field(default_factory=dict)
    remainder: Dict[str, str] = field(default_factory=dict)

    def bucket_names(self) -> List[str]:
        return list(self.buckets.keys())

    def summary(self) -> str:
        lines = []
        for name, bucket in self.buckets.items():
            lines.append(f"{name}: {len(bucket)} key(s)")
        lines.append(f"remainder: {len(self.remainder)} key(s)")
        return "\n".join(lines)


def split_env(
    env: Dict[str, str],
    rules: List[Tuple[str, str]],
    *,
    use_regex: bool = False,
    keep_remainder: bool = True,
) -> SplitResult:
    """Split *env* into named buckets according to *rules*.

    Each rule is a ``(bucket_name, pattern)`` pair.  Keys are matched against
    patterns in order; the first match wins.  Unmatched keys land in
    ``SplitResult.remainder`` when *keep_remainder* is ``True``.
    """
    result = SplitResult()
    for bucket_name, _ in rules:
        if bucket_name not in result.buckets:
            result.buckets[bucket_name] = SplitBucket(name=bucket_name)

    compiled: List[Tuple[str, re.Pattern]] = []
    for bucket_name, pattern in rules:
        if use_regex:
            compiled.append((bucket_name, re.compile(pattern)))
        else:
            # Treat pattern as a prefix (case-insensitive)
            escaped = re.escape(pattern)
            compiled.append((bucket_name, re.compile(f"^{escaped}", re.IGNORECASE)))

    for key, value in env.items():
        matched: Optional[str] = None
        for bucket_name, rx in compiled:
            if rx.search(key):
                matched = bucket_name
                break
        if matched is not None:
            result.buckets[matched].env[key] = value
        elif keep_remainder:
            result.remainder[key] = value

    return result
