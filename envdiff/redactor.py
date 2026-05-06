"""Redact sensitive environment variable values before display or export."""

import re
from typing import Dict, List, Optional

# Default patterns that indicate a key likely holds a sensitive value
DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE_KEY.*",
    r".*CREDENTIALS.*",
    r".*AUTH.*",
]

REDACT_PLACEHOLDER = "***REDACTED***"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def is_sensitive(key: str, patterns: Optional[List[str]] = None) -> bool:
    """Return True if *key* matches any of the given (or default) sensitive patterns."""
    compiled = _compile_patterns(patterns if patterns is not None else DEFAULT_SENSITIVE_PATTERNS)
    return any(pat.fullmatch(key) for pat in compiled)


def redact_env(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values replaced by *placeholder*."""
    return {
        key: (placeholder if is_sensitive(key, patterns) else value)
        for key, value in env.items()
    }


def redact_value(
    key: str,
    value: str,
    patterns: Optional[List[str]] = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> str:
    """Return *placeholder* if *key* is sensitive, otherwise return *value* unchanged."""
    return placeholder if is_sensitive(key, patterns) else value
