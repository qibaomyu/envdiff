"""Tag environment variables with user-defined labels for categorisation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class TagEntry:
    key: str
    value: str
    tags: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"TagEntry(key={self.key!r}, tags={self.tags!r})"


@dataclass
class TaggedEnv:
    entries: List[TagEntry] = field(default_factory=list)

    def by_tag(self, tag: str) -> List[TagEntry]:
        """Return all entries that carry *tag*."""
        return [e for e in self.entries if tag in e.tags]

    def all_tags(self) -> List[str]:
        """Return a sorted, deduplicated list of every tag present."""
        seen: set = set()
        for entry in self.entries:
            seen.update(entry.tags)
        return sorted(seen)

    def summary(self) -> Dict[str, int]:
        """Return a mapping of tag -> count of entries carrying that tag."""
        result: Dict[str, int] = {}
        for tag in self.all_tags():
            result[tag] = len(self.by_tag(tag))
        return result


def tag_env(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
    *,
    default_tags: Optional[List[str]] = None,
) -> TaggedEnv:
    """Tag every key in *env* according to *rules*.

    *rules* maps a regex pattern to the list of tags to apply when the
    pattern matches the key name.  A key may match multiple patterns and
    accumulate tags from all of them.  *default_tags* are applied to keys
    that match no rule at all.
    """
    compiled = [(re.compile(pat), tags) for pat, tags in rules.items()]
    entries: List[TagEntry] = []

    for key, value in env.items():
        applied: List[str] = []
        for pattern, tags in compiled:
            if pattern.search(key):
                for t in tags:
                    if t not in applied:
                        applied.append(t)
        if not applied and default_tags:
            applied = list(default_tags)
        entries.append(TagEntry(key=key, value=value, tags=applied))

    return TaggedEnv(entries=entries)
