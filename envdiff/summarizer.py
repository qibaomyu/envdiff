"""Summarizer: produce a high-level statistical summary of an env mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EnvSummary:
    total: int
    empty_count: int
    non_empty_count: int
    unique_values: int
    duplicate_values: int
    longest_key: str
    shortest_key: str
    longest_value_key: str
    avg_value_length: float
    key_lengths: List[int] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"EnvSummary(total={self.total}, empty={self.empty_count}, "
            f"unique_values={self.unique_values})"
        )


def summarize_env(env: Dict[str, str]) -> EnvSummary:
    """Return an :class:`EnvSummary` for *env*."""
    if not env:
        return EnvSummary(
            total=0,
            empty_count=0,
            non_empty_count=0,
            unique_values=0,
            duplicate_values=0,
            longest_key="",
            shortest_key="",
            longest_value_key="",
            avg_value_length=0.0,
            key_lengths=[],
        )

    keys = list(env.keys())
    values = list(env.values())

    empty_count = sum(1 for v in values if v == "")
    non_empty_count = len(values) - empty_count

    value_counts: Dict[str, int] = {}
    for v in values:
        value_counts[v] = value_counts.get(v, 0) + 1

    unique_values = sum(1 for c in value_counts.values() if c == 1)
    duplicate_values = len(value_counts) - unique_values

    longest_key = max(keys, key=len)
    shortest_key = min(keys, key=len)
    longest_value_key = max(keys, key=lambda k: len(env[k]))

    total_value_len = sum(len(v) for v in values)
    avg_value_length = total_value_len / len(values)

    key_lengths = sorted(len(k) for k in keys)

    return EnvSummary(
        total=len(env),
        empty_count=empty_count,
        non_empty_count=non_empty_count,
        unique_values=unique_values,
        duplicate_values=duplicate_values,
        longest_key=longest_key,
        shortest_key=shortest_key,
        longest_value_key=longest_value_key,
        avg_value_length=round(avg_value_length, 2),
        key_lengths=key_lengths,
    )


def text_summary(summary: EnvSummary) -> str:
    """Render *summary* as a human-readable string."""
    lines = [
        f"Total keys       : {summary.total}",
        f"Empty values     : {summary.empty_count}",
        f"Non-empty values : {summary.non_empty_count}",
        f"Unique values    : {summary.unique_values}",
        f"Duplicate values : {summary.duplicate_values}",
        f"Longest key      : {summary.longest_key}",
        f"Shortest key     : {summary.shortest_key}",
        f"Longest value key: {summary.longest_value_key}",
        f"Avg value length : {summary.avg_value_length}",
    ]
    return "\n".join(lines)
