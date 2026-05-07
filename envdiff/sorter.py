"""Sort and rank environment variables by various criteria."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortBy(str, Enum):
    KEY = "key"
    VALUE_LENGTH = "value_length"
    VALUE = "value"


@dataclass
class SortedEnv:
    entries: List[tuple] = field(default_factory=list)
    sort_by: SortBy = SortBy.KEY
    order: SortOrder = SortOrder.ASC

    def keys(self) -> List[str]:
        return [k for k, _ in self.entries]

    def as_dict(self) -> Dict[str, str]:
        return dict(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:  # pragma: no cover
        return f"SortedEnv(count={len(self)}, sort_by={self.sort_by}, order={self.order})"


def sort_env(
    env: Dict[str, str],
    sort_by: SortBy = SortBy.KEY,
    order: SortOrder = SortOrder.ASC,
) -> SortedEnv:
    """Return a SortedEnv with entries ordered by the given criterion."""
    reverse = order == SortOrder.DESC

    if sort_by == SortBy.KEY:
        key_fn = lambda item: item[0].lower()
    elif sort_by == SortBy.VALUE_LENGTH:
        key_fn = lambda item: len(item[1])
    elif sort_by == SortBy.VALUE:
        key_fn = lambda item: item[1].lower()
    else:
        raise ValueError(f"Unknown sort_by: {sort_by}")

    sorted_items = sorted(env.items(), key=key_fn, reverse=reverse)
    return SortedEnv(entries=sorted_items, sort_by=sort_by, order=order)


def rank_by_value_length(
    env: Dict[str, str], top_n: int = 10
) -> List[tuple]:
    """Return the top_n keys with the longest values."""
    sorted_items = sorted(env.items(), key=lambda item: len(item[1]), reverse=True)
    return sorted_items[:top_n]
