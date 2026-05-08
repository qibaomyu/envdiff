"""Transform environment variable values using configurable rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformEntry:
    key: str
    original: str
    transformed: str
    rule_applied: str

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TransformEntry(key={self.key!r}, rule={self.rule_applied!r}, "
            f"{self.original!r} -> {self.transformed!r})"
        )


@dataclass
class TransformResult:
    entries: List[TransformEntry] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def changed(self) -> List[TransformEntry]:
        """Return only entries where the value actually changed."""
        return [e for e in self.entries if e.original != e.transformed]

    def unchanged(self) -> List[TransformEntry]:
        """Return entries where the value was not changed."""
        return [e for e in self.entries if e.original == e.transformed]

    def summary(self) -> str:
        n = len(self.changed())
        total = len(self.entries)
        return f"{n}/{total} keys transformed"


# Built-in transform rules
def _rule_uppercase(value: str) -> str:
    return value.upper()


def _rule_lowercase(value: str) -> str:
    return value.lower()


def _rule_strip(value: str) -> str:
    return value.strip()


def _rule_strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


BUILT_IN_RULES: Dict[str, Callable[[str], str]] = {
    "uppercase": _rule_uppercase,
    "lowercase": _rule_lowercase,
    "strip": _rule_strip,
    "strip_quotes": _rule_strip_quotes,
}


def transform_env(
    env: Dict[str, str],
    rules: List[str],
    keys: Optional[List[str]] = None,
    custom_rules: Optional[Dict[str, Callable[[str], str]]] = None,
) -> TransformResult:
    """Apply a sequence of named rules to env values.

    Args:
        env: The source environment mapping.
        rules: Ordered list of rule names to apply.
        keys: If provided, only transform these keys; otherwise all keys.
        custom_rules: Additional named transform callables.

    Returns:
        A TransformResult containing per-key entries and the final env dict.
    """
    all_rules = {**BUILT_IN_RULES, **(custom_rules or {})}

    unknown = [r for r in rules if r not in all_rules]
    if unknown:
        raise ValueError(f"Unknown transform rules: {unknown}")

    target_keys = set(keys) if keys is not None else set(env.keys())
    result_env: Dict[str, str] = dict(env)
    entries: List[TransformEntry] = []

    for key in sorted(env.keys()):
        original = env[key]
        if key in target_keys:
            value = original
            applied = "+".join(rules) if rules else "identity"
            for rule_name in rules:
                value = all_rules[rule_name](value)
            result_env[key] = value
            entries.append(TransformEntry(key, original, value, applied))
        else:
            entries.append(TransformEntry(key, original, original, "skipped"))

    return TransformResult(entries=entries, env=result_env)
