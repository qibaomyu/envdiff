"""Template rendering for env files — fill a template with values from an env dict."""

from __future__ import annotations

import re
from typing import Dict, Optional

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class TemplateRenderError(Exception):
    """Raised when a required placeholder cannot be resolved."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Template placeholder '{key}' has no value in the provided env")


def find_placeholders(template: str) -> list[str]:
    """Return a list of unique placeholder names found in *template*."""
    seen: list[str] = []
    for match in _PLACEHOLDER_RE.finditer(template):
        name = match.group(1)
        if name not in seen:
            seen.append(name)
    return seen


def render_template(
    template: str,
    env: Dict[str, str],
    *,
    default: Optional[str] = None,
    strict: bool = True,
) -> str:
    """Replace ``{{ KEY }}`` placeholders in *template* with values from *env*.

    Parameters
    ----------
    template:
        The template string containing ``{{ KEY }}`` placeholders.
    env:
        Mapping of variable names to values used for substitution.
    default:
        Fallback value used when a key is missing and *strict* is ``False``.
    strict:
        When ``True`` (default) raise :class:`TemplateRenderError` for any
        missing key.  When ``False`` use *default* instead.
    """

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        if key in env:
            return env[key]
        if not strict:
            return default if default is not None else match.group(0)
        raise TemplateRenderError(key)

    return _PLACEHOLDER_RE.sub(_replace, template)


def render_template_file(
    template_path: str,
    env: Dict[str, str],
    *,
    default: Optional[str] = None,
    strict: bool = True,
) -> str:
    """Read *template_path* from disk and delegate to :func:`render_template`."""
    with open(template_path, "r", encoding="utf-8") as fh:
        template = fh.read()
    return render_template(template, env, default=default, strict=strict)
