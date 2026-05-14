"""Inspector: deep-inspect a single env dict and produce a structured report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InspectEntry:
    key: str
    value: str
    length: int
    is_empty: bool
    is_numeric: bool
    is_boolean: bool
    is_url: bool
    is_path: bool
    has_whitespace: bool
    has_special_chars: bool

    def __repr__(self) -> str:  # pragma: no cover
        return f"InspectEntry(key={self.key!r}, length={self.length})"


@dataclass
class InspectResult:
    entries: List[InspectEntry] = field(default_factory=list)

    def by_key(self, key: str) -> Optional[InspectEntry]:
        for e in self.entries:
            if e.key == key:
                return e
        return None

    def summary(self) -> Dict[str, int]:
        total = len(self.entries)
        return {
            "total": total,
            "empty": sum(1 for e in self.entries if e.is_empty),
            "numeric": sum(1 for e in self.entries if e.is_numeric),
            "boolean": sum(1 for e in self.entries if e.is_boolean),
            "url": sum(1 for e in self.entries if e.is_url),
            "path": sum(1 for e in self.entries if e.is_path),
            "has_whitespace": sum(1 for e in self.entries if e.has_whitespace),
            "has_special_chars": sum(1 for e in self.entries if e.has_special_chars),
        }


_BOOLEAN_VALUES = {"true", "false", "yes", "no", "1", "0", "on", "off"}
_SPECIAL_CHARS = set("!@#$%^&*()[]{}<>?|;,`~'\"")


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _is_boolean(value: str) -> bool:
    return value.strip().lower() in _BOOLEAN_VALUES


def _is_url(value: str) -> bool:
    return value.startswith(("http://", "https://", "ftp://", "redis://", "postgres://", "mysql://"))


def _is_path(value: str) -> bool:
    return value.startswith("/") or value.startswith("./") or value.startswith("../")


def inspect_env(env: Dict[str, str]) -> InspectResult:
    """Inspect each key/value pair and return an InspectResult."""
    entries: List[InspectEntry] = []
    for key, value in env.items():
        entries.append(
            InspectEntry(
                key=key,
                value=value,
                length=len(value),
                is_empty=value == "",
                is_numeric=_is_numeric(value) if value else False,
                is_boolean=_is_boolean(value) if value else False,
                is_url=_is_url(value),
                is_path=_is_path(value),
                has_whitespace=any(c in value for c in (" ", "\t", "\n")),
                has_special_chars=any(c in _SPECIAL_CHARS for c in value),
            )
        )
    return InspectResult(entries=entries)
