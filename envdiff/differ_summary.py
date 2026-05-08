"""Summarizes a DiffChangelog into human-readable or structured output."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.differ import DiffChangelog, ChangeEntry


@dataclass
class DiffSummary:
    total: int
    added: int
    removed: int
    modified: int
    unchanged: int
    by_type: Dict[str, List[ChangeEntry]] = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DiffSummary(total={self.total}, added={self.added}, "
            f"removed={self.removed}, modified={self.modified}, "
            f"unchanged={self.unchanged})"
        )


def summarize_diff(changelog: DiffChangelog) -> DiffSummary:
    """Return a structured summary of a DiffChangelog."""
    by_type: Dict[str, List[ChangeEntry]] = {
        "added": [],
        "removed": [],
        "modified": [],
        "unchanged": [],
    }
    for entry in changelog.all_entries():
        bucket = by_type.get(entry.change_type)
        if bucket is not None:
            bucket.append(entry)

    return DiffSummary(
        total=sum(len(v) for v in by_type.values()),
        added=len(by_type["added"]),
        removed=len(by_type["removed"]),
        modified=len(by_type["modified"]),
        unchanged=len(by_type["unchanged"]),
        by_type=by_type,
    )


def text_diff_summary(summary: DiffSummary) -> str:
    """Render a DiffSummary as a plain-text block."""
    lines = [
        f"Total keys : {summary.total}",
        f"  Added    : {summary.added}",
        f"  Removed  : {summary.removed}",
        f"  Modified : {summary.modified}",
        f"  Unchanged: {summary.unchanged}",
    ]
    return "\n".join(lines)
