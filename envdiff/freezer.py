"""Freeze an env snapshot to a locked file, preventing future drift."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

FREEZE_VERSION = "1"


@dataclass
class FreezeViolation:
    key: str
    expected: str
    actual: Optional[str]  # None means key is missing

    def __repr__(self) -> str:  # pragma: no cover
        return f"FreezeViolation(key={self.key!r}, expected={self.expected!r}, actual={self.actual!r})"


@dataclass
class FreezeResult:
    frozen_keys: List[str]
    violations: List[FreezeViolation] = field(default_factory=list)

    def has_violations(self) -> bool:
        return bool(self.violations)

    def summary(self) -> str:
        if not self.has_violations():
            return f"OK — {len(self.frozen_keys)} key(s) match frozen values."
        lines = [f"{len(self.violations)} violation(s) against frozen env:"]
        for v in self.violations:
            actual_str = repr(v.actual) if v.actual is not None else "<missing>"
            lines.append(f"  {v.key}: expected {v.expected!r}, got {actual_str}")
        return "\n".join(lines)


def freeze_env(env: Dict[str, str], path: str, label: str = "") -> None:
    """Write a freeze file containing the locked key/value pairs."""
    payload = {
        "version": FREEZE_VERSION,
        "label": label,
        "env": env,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


def load_freeze(path: str) -> Dict[str, str]:
    """Load frozen env from a freeze file. Returns the env dict."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Freeze file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("version") != FREEZE_VERSION:
        raise ValueError(f"Unsupported freeze file version: {data.get('version')!r}")
    return {str(k): str(v) for k, v in data.get("env", {}).items()}


def check_freeze(frozen: Dict[str, str], actual: Dict[str, str]) -> FreezeResult:
    """Compare actual env against frozen values; return FreezeResult."""
    violations: List[FreezeViolation] = []
    for key, expected in frozen.items():
        got = actual.get(key)
        if got != expected:
            violations.append(FreezeViolation(key=key, expected=expected, actual=got))
    return FreezeResult(frozen_keys=list(frozen.keys()), violations=violations)
