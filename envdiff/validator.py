"""Validate environment variable keys and values against rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValidationIssue:
    key: str
    message: str
    severity: str = "error"  # "error" or "warning"

    def __repr__(self) -> str:
        return f"ValidationIssue({self.severity}: {self.key!r} — {self.message})"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


_VALID_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_env(
    env: Dict[str, str],
    required_keys: Optional[List[str]] = None,
    forbidden_keys: Optional[List[str]] = None,
    no_empty_values: bool = False,
) -> ValidationResult:
    """Validate an environment dict against a set of rules."""
    result = ValidationResult()

    for key in env:
        if not _VALID_KEY_RE.match(key):
            result.issues.append(
                ValidationIssue(key, f"Key {key!r} contains invalid characters.")
            )

    if required_keys:
        for key in required_keys:
            if key not in env:
                result.issues.append(
                    ValidationIssue(key, f"Required key {key!r} is missing.", "error")
                )

    if forbidden_keys:
        for key in forbidden_keys:
            if key in env:
                result.issues.append(
                    ValidationIssue(key, f"Forbidden key {key!r} is present.", "error")
                )

    if no_empty_values:
        for key, value in env.items():
            if value == "":
                result.issues.append(
                    ValidationIssue(key, f"Key {key!r} has an empty value.", "warning")
                )

    return result
