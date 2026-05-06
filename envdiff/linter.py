"""Lint environment variable definitions for style and convention issues."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_UPPER_SNAKE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_HAS_LOWER = re.compile(r'[a-z]')
_DOUBLE_UNDERSCORE = re.compile(r'__')
_LEADING_DIGIT = re.compile(r'^[0-9]')


@dataclass
class LintIssue:
    key: str
    code: str
    message: str
    severity: str = "warning"  # "warning" or "error"

    def __repr__(self) -> str:
        return f"LintIssue({self.severity.upper()} [{self.code}] {self.key!r}: {self.message})"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def summary(self) -> str:
        e = len(self.errors())
        w = len(self.warnings())
        return f"{e} error(s), {w} warning(s)"


def lint_env(env: Dict[str, str], allow_lowercase: bool = False) -> LintResult:
    """Run all lint checks against an env dict and return a LintResult."""
    result = LintResult()
    for key, value in env.items():
        result.issues.extend(_check_key(key, allow_lowercase))
        result.issues.extend(_check_value(key, value))
    return result


def _check_key(key: str, allow_lowercase: bool) -> List[LintIssue]:
    issues: List[LintIssue] = []

    if _LEADING_DIGIT.match(key):
        issues.append(LintIssue(key, "E001", "Key must not start with a digit.", "error"))

    if not allow_lowercase and _HAS_LOWER.search(key):
        issues.append(LintIssue(key, "W001", "Key contains lowercase letters; prefer UPPER_SNAKE_CASE."))

    if _DOUBLE_UNDERSCORE.search(key):
        issues.append(LintIssue(key, "W002", "Key contains consecutive underscores."))

    if key != key.strip():
        issues.append(LintIssue(key, "E002", "Key has leading or trailing whitespace.", "error"))

    return issues


def _check_value(key: str, value: str) -> List[LintIssue]:
    issues: List[LintIssue] = []

    if value != value.strip():
        issues.append(LintIssue(key, "W003", "Value has leading or trailing whitespace."))

    if value == "":
        issues.append(LintIssue(key, "W004", "Value is empty."))

    if value.startswith('"') and not value.endswith('"'):
        issues.append(LintIssue(key, "W005", "Value appears to have unmatched double-quote."))

    if value.startswith("'") and not value.endswith("'"):
        issues.append(LintIssue(key, "W005", "Value appears to have unmatched single-quote."))

    return issues
