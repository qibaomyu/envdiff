"""Diff two snapshots or env dicts and produce a structured changelog."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ChangeEntry:
    key: str
    change_type: str  # 'added', 'removed', 'modified', 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ChangeEntry(key={self.key!r}, type={self.change_type!r}, "
            f"old={self.old_value!r}, new={self.new_value!r})"
        )


@dataclass
class DiffChangelog:
    added: List[ChangeEntry] = field(default_factory=list)
    removed: List[ChangeEntry] = field(default_factory=list)
    modified: List[ChangeEntry] = field(default_factory=list)
    unchanged: List[ChangeEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def all_entries(self) -> List[ChangeEntry]:
        return self.added + self.removed + self.modified + self.unchanged


def diff_snapshots(
    before: Dict[str, str],
    after: Dict[str, str],
    include_unchanged: bool = False,
) -> DiffChangelog:
    """Compare two env dicts (e.g. loaded snapshots) and return a DiffChangelog."""
    changelog = DiffChangelog()
    all_keys = set(before) | set(after)

    for key in sorted(all_keys):
        in_before = key in before
        in_after = key in after

        if in_before and not in_after:
            changelog.removed.append(
                ChangeEntry(key=key, change_type="removed", old_value=before[key])
            )
        elif in_after and not in_before:
            changelog.added.append(
                ChangeEntry(key=key, change_type="added", new_value=after[key])
            )
        elif before[key] != after[key]:
            changelog.modified.append(
                ChangeEntry(
                    key=key,
                    change_type="modified",
                    old_value=before[key],
                    new_value=after[key],
                )
            )
        elif include_unchanged:
            changelog.unchanged.append(
                ChangeEntry(
                    key=key,
                    change_type="unchanged",
                    old_value=before[key],
                    new_value=after[key],
                )
            )

    return changelog


def format_changelog(changelog: DiffChangelog, label_before: str = "before", label_after: str = "after") -> str:
    """Render a human-readable changelog string."""
    lines: List[str] = [f"Changelog ({label_before} -> {label_after}):", ""]

    for entry in changelog.added:
        lines.append(f"  + {entry.key} = {entry.new_value}")
    for entry in changelog.removed:
        lines.append(f"  - {entry.key} (was: {entry.old_value})")
    for entry in changelog.modified:
        lines.append(f"  ~ {entry.key}: {entry.old_value!r} -> {entry.new_value!r}")

    if not changelog.has_changes:
        lines.append("  (no changes)")

    return "\n".join(lines)
