"""Scores environment configurations based on quality heuristics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.redactor import is_sensitive


@dataclass
class ScoreBreakdown:
    total_keys: int = 0
    empty_values: int = 0
    sensitive_unredacted: int = 0
    suspicious_keys: int = 0
    penalties: List[str] = field(default_factory=list)

    def score(self) -> float:
        """Return a quality score between 0.0 and 100.0."""
        if self.total_keys == 0:
            return 100.0
        penalty = 0.0
        if self.empty_values:
            penalty += (self.empty_values / self.total_keys) * 30
        if self.sensitive_unredacted:
            penalty += (self.sensitive_unredacted / self.total_keys) * 40
        if self.suspicious_keys:
            penalty += (self.suspicious_keys / self.total_keys) * 20
        return max(0.0, round(100.0 - penalty, 2))

    def grade(self) -> str:
        s = self.score()
        if s >= 90:
            return "A"
        if s >= 75:
            return "B"
        if s >= 60:
            return "C"
        if s >= 40:
            return "D"
        return "F"


_SUSPICIOUS_PATTERNS = ("todo", "fixme", "changeme", "placeholder", "example", "test")


def _is_suspicious_value(value: str) -> bool:
    lower = value.lower()
    return any(p in lower for p in _SUSPICIOUS_PATTERNS)


def score_env(env: Dict[str, str]) -> ScoreBreakdown:
    """Analyse *env* and return a ScoreBreakdown."""
    breakdown = ScoreBreakdown(total_keys=len(env))

    for key, value in env.items():
        if value == "":
            breakdown.empty_values += 1
            breakdown.penalties.append(f"Empty value for key: {key}")

        if is_sensitive(key) and value not in ("", "***", "[REDACTED]"):
            breakdown.sensitive_unredacted += 1
            breakdown.penalties.append(f"Sensitive key may be unredacted: {key}")

        if _is_suspicious_value(value):
            breakdown.suspicious_keys += 1
            breakdown.penalties.append(f"Suspicious placeholder value for key: {key}")

    return breakdown
