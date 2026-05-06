"""Interpolator: resolves ${VAR} references within environment variable values."""

import re
from typing import Dict, Optional

_REF_PATTERN = re.compile(r"\$\{([^}]+)\}")


class InterpolationError(Exception):
    """Raised when a variable reference cannot be resolved."""


def find_references(value: str) -> list[str]:
    """Return all variable names referenced inside *value*."""
    return _REF_PATTERN.findall(value)


def interpolate_value(
    value: str,
    env: Dict[str, str],
    *,
    strict: bool = False,
    _seen: Optional[set] = None,
) -> str:
    """Replace ``${VAR}`` placeholders in *value* using *env*.

    Parameters
    ----------
    value:  The raw string that may contain ``${VAR}`` references.
    env:    Mapping used to look up referenced variable names.
    strict: When *True*, raise :class:`InterpolationError` for missing keys;
            otherwise leave the placeholder unchanged.
    """
    if _seen is None:
        _seen = set()

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key in _seen:
            raise InterpolationError(f"Circular reference detected for key '{key}'")
        if key not in env:
            if strict:
                raise InterpolationError(f"Undefined variable reference: '{key}'")
            return match.group(0)  # leave placeholder intact
        _seen_next = _seen | {key}
        return interpolate_value(env[key], env, strict=strict, _seen=_seen_next)

    return _REF_PATTERN.sub(_replace, value)


def interpolate_env(
    env: Dict[str, str],
    *,
    strict: bool = False,
) -> Dict[str, str]:
    """Return a new dict where all values have been interpolated.

    Entries whose values contain no references are returned unchanged.
    """
    return {
        key: interpolate_value(value, env, strict=strict)
        for key, value in env.items()
    }
