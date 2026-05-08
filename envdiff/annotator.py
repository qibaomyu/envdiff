"""Annotate environment variables with inline comments or metadata."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AnnotationEntry:
    key: str
    value: str
    comment: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"AnnotationEntry(key={self.key!r}, comment={self.comment!r})"


@dataclass
class AnnotationResult:
    entries: List[AnnotationEntry] = field(default_factory=list)
    unannotated: List[str] = field(default_factory=list)

    def by_key(self, key: str) -> Optional[AnnotationEntry]:
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None

    def has_annotations(self) -> bool:
        return len(self.entries) > 0

    def summary(self) -> str:
        total = len(self.entries) + len(self.unannotated)
        return (
            f"{len(self.entries)} annotated, "
            f"{len(self.unannotated)} unannotated out of {total} keys"
        )


def annotate_env(
    env: Dict[str, str],
    rules: Dict[str, str],
) -> AnnotationResult:
    """Attach a comment string to each key that matches a rule.

    Args:
        env:   Mapping of key -> value to annotate.
        rules: Mapping of key -> comment string. Keys not present in
               *rules* are placed in ``unannotated``.

    Returns:
        An :class:`AnnotationResult` with populated entries.
    """
    entries: List[AnnotationEntry] = []
    unannotated: List[str] = []

    for key, value in env.items():
        if key in rules:
            entries.append(AnnotationEntry(key=key, value=value, comment=rules[key]))
        else:
            unannotated.append(key)

    return AnnotationResult(entries=entries, unannotated=unannotated)


def render_annotated_dotenv(result: AnnotationResult) -> str:
    """Render an annotated env as a .env-style string with inline comments."""
    lines: List[str] = []
    for entry in result.entries:
        lines.append(f"# {entry.comment}")
        lines.append(f"{entry.key}={entry.value}")
    for key in result.unannotated:
        # Find value — stored only in unannotated list (key only), skip value here
        lines.append(f"{key}=")
    return "\n".join(lines)
