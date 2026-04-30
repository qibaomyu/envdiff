"""Formats and outputs EnvDiffResult comparisons in human-readable or machine-readable formats."""

from __future__ import annotations

import json
from enum import Enum
from typing import TextIO
import sys

from envdiff.comparator import EnvDiffResult


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


def _text_report(result: EnvDiffResult, label_a: str, label_b: str) -> str:
    lines: list[str] = []
    lines.append(f"=== EnvDiff Report: {label_a!r} vs {label_b!r} ===")

    if result.only_in_a:
        lines.append(f"\nOnly in {label_a!r}:")
        for key in sorted(result.only_in_a):
            lines.append(f"  - {key}")

    if result.only_in_b:
        lines.append(f"\nOnly in {label_b!r}:")
        for key in sorted(result.only_in_b):
            lines.append(f"  + {key}")

    if result.value_differs:
        lines.append("\nValue differences:")
        for key in sorted(result.value_differs):
            val_a, val_b = result.value_differs[key]
            lines.append(f"  ~ {key}")
            lines.append(f"      {label_a}: {val_a!r}")
            lines.append(f"      {label_b}: {val_b!r}")

    if not (result.only_in_a or result.only_in_b or result.value_differs):
        lines.append("\nNo differences found.")

    return "\n".join(lines)


def _json_report(result: EnvDiffResult, label_a: str, label_b: str) -> str:
    payload = {
        "targets": {"a": label_a, "b": label_b},
        "only_in_a": sorted(result.only_in_a),
        "only_in_b": sorted(result.only_in_b),
        "value_differs": {
            key: {label_a: va, label_b: vb}
            for key, (va, vb) in sorted(result.value_differs.items())
        },
        "has_differences": bool(
            result.only_in_a or result.only_in_b or result.value_differs
        ),
    }
    return json.dumps(payload, indent=2)


def render(
    result: EnvDiffResult,
    label_a: str = "A",
    label_b: str = "B",
    fmt: OutputFormat = OutputFormat.TEXT,
    out: TextIO = sys.stdout,
) -> None:
    """Render an EnvDiffResult to *out* using the requested format."""
    if fmt == OutputFormat.JSON:
        output = _json_report(result, label_a, label_b)
    else:
        output = _text_report(result, label_a, label_b)
    out.write(output + "\n")
