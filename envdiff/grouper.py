"""Group environment variables by prefix or pattern."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvGroup:
    """A named group of environment variable keys."""

    name: str
    keys: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"EnvGroup(name={self.name!r}, keys={self.keys!r})"

    def __len__(self) -> int:
        return len(self.keys)


def group_by_prefix(
    env: Dict[str, str],
    separator: str = "_",
    min_group_size: int = 1,
) -> Dict[str, EnvGroup]:
    """Group keys by their first prefix segment.

    Keys without a separator are placed in the '__ungrouped__' group.
    Groups smaller than *min_group_size* are merged into '__ungrouped__'.
    """
    buckets: Dict[str, List[str]] = defaultdict(list)
    for key in env:
        if separator in key:
            prefix = key.split(separator, 1)[0]
        else:
            prefix = "__ungrouped__"
        buckets[prefix].append(key)

    groups: Dict[str, EnvGroup] = {}
    ungrouped: List[str] = list(buckets.pop("__ungrouped__", []))

    for prefix, keys in buckets.items():
        if len(keys) < min_group_size:
            ungrouped.extend(keys)
        else:
            groups[prefix] = EnvGroup(name=prefix, keys=sorted(keys))

    if ungrouped:
        groups["__ungrouped__"] = EnvGroup(
            name="__ungrouped__", keys=sorted(ungrouped)
        )

    return groups


def group_by_regex(
    env: Dict[str, str],
    patterns: Dict[str, str],
    fallback_group: str = "__other__",
) -> Dict[str, EnvGroup]:
    """Group keys by matching against named regex patterns.

    *patterns* maps group name -> regex string.  The first matching pattern
    wins.  Unmatched keys land in *fallback_group*.
    """
    compiled = {name: re.compile(pat) for name, pat in patterns.items()}
    buckets: Dict[str, List[str]] = defaultdict(list)

    for key in env:
        matched = False
        for name, rx in compiled.items():
            if rx.search(key):
                buckets[name].append(key)
                matched = True
                break
        if not matched:
            buckets[fallback_group].append(key)

    return {
        name: EnvGroup(name=name, keys=sorted(keys))
        for name, keys in buckets.items()
    }
