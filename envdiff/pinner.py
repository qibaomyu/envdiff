"""Pin environment variable values to a reference snapshot for drift detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinViolation:
    key: str
    pinned_value: str
    actual_value: Optional[str]
    reason: str  # 'changed' | 'missing' | 'unexpected'

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PinViolation(key={self.key!r}, reason={self.reason!r}, "
            f"pinned={self.pinned_value!r}, actual={self.actual_value!r})"
        )


@dataclass
class PinResult:
    violations: List[PinViolation] = field(default_factory=list)
    pinned_keys: List[str] = field(default_factory=list)

    def has_violations(self) -> bool:
        return bool(self.violations)

    def summary(self) -> str:
        if not self.has_violations():
            return f"All {len(self.pinned_keys)} pinned key(s) match."
        lines = [f"{len(self.violations)} violation(s) detected:"]
        for v in self.violations:
            lines.append(f"  [{v.reason.upper()}] {v.key}: {v.pinned_value!r} -> {v.actual_value!r}")
        return "\n".join(lines)


def pin_env(
    pinned: Dict[str, str],
    actual: Dict[str, str],
    *,
    allow_extra: bool = True,
) -> PinResult:
    """Compare *actual* env against a *pinned* reference.

    Args:
        pinned: The reference key/value pairs that must be matched.
        actual: The environment under test.
        allow_extra: When False, keys present in *actual* but absent from
            *pinned* are reported as 'unexpected' violations.

    Returns:
        A :class:`PinResult` describing any drift.
    """
    violations: List[PinViolation] = []

    for key, expected_val in pinned.items():
        if key not in actual:
            violations.append(
                PinViolation(
                    key=key,
                    pinned_value=expected_val,
                    actual_value=None,
                    reason="missing",
                )
            )
        elif actual[key] != expected_val:
            violations.append(
                PinViolation(
                    key=key,
                    pinned_value=expected_val,
                    actual_value=actual[key],
                    reason="changed",
                )
            )

    if not allow_extra:
        for key in actual:
            if key not in pinned:
                violations.append(
                    PinViolation(
                        key=key,
                        pinned_value="",
                        actual_value=actual[key],
                        reason="unexpected",
                    )
                )

    return PinResult(violations=violations, pinned_keys=list(pinned.keys()))
