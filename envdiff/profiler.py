"""Profile environment variables by categorizing and scoring them."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Category patterns: (category_name, list of key substrings)
_CATEGORY_PATTERNS: List[tuple] = [
    ("database", ["DB", "DATABASE", "POSTGRES", "MYSQL", "MONGO", "REDIS", "SQLITE"]),
    ("auth", ["SECRET", "TOKEN", "API_KEY", "PASSWORD", "PASSWD", "AUTH", "JWT"]),
    ("network", ["HOST", "PORT", "URL", "URI", "ENDPOINT", "ADDR", "DOMAIN"]),
    ("logging", ["LOG", "DEBUG", "VERBOSE", "TRACE", "SENTRY"]),
    ("feature", ["FEATURE", "FLAG", "ENABLE", "DISABLE", "TOGGLE"]),
    ("infra", ["AWS", "GCP", "AZURE", "S3", "BUCKET", "REGION", "CLUSTER"]),
]


@dataclass
class ProfileEntry:
    key: str
    value: str
    category: str
    is_empty: bool
    length: int

    def __repr__(self) -> str:
        return f"ProfileEntry(key={self.key!r}, category={self.category!r}, is_empty={self.is_empty})"


@dataclass
class EnvProfile:
    entries: List[ProfileEntry] = field(default_factory=list)
    total: int = 0
    empty_count: int = 0
    categories: Dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Total keys   : {self.total}",
            f"Empty values : {self.empty_count}",
            "Categories   :",
        ]
        for cat, count in sorted(self.categories.items()):
            lines.append(f"  {cat:<14}: {count}")
        return "\n".join(lines)


def _categorize(key: str) -> str:
    upper = key.upper()
    for category, patterns in _CATEGORY_PATTERNS:
        if any(p in upper for p in patterns):
            return category
    return "general"


def profile_env(env: Dict[str, str]) -> EnvProfile:
    """Build an EnvProfile from a flat env dict."""
    entries: List[ProfileEntry] = []
    categories: Dict[str, int] = {}

    for key, value in env.items():
        cat = _categorize(key)
        is_empty = value.strip() == ""
        entry = ProfileEntry(
            key=key,
            value=value,
            category=cat,
            is_empty=is_empty,
            length=len(value),
        )
        entries.append(entry)
        categories[cat] = categories.get(cat, 0) + 1

    empty_count = sum(1 for e in entries if e.is_empty)
    return EnvProfile(
        entries=entries,
        total=len(entries),
        empty_count=empty_count,
        categories=categories,
    )
