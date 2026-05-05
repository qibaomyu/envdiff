"""Export environment diff results to various file formats."""

from __future__ import annotations

import csv
import io
import json
from enum import Enum
from pathlib import Path
from typing import Optional

from envdiff.comparator import EnvDiffResult


class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    DOTENV = "dotenv"


def _export_csv(result: EnvDiffResult, label_a: str, label_b: str) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["key", "status", label_a, label_b])

    for key in sorted(result.only_in_a):
        writer.writerow([key, "only_in_a", result.env_a[key], ""])

    for key in sorted(result.only_in_b):
        writer.writerow([key, "only_in_b", "", result.env_b[key]])

    for key in sorted(result.value_differs):
        writer.writerow([key, "value_differs", result.env_a[key], result.env_b[key]])

    for key in sorted(result.common_keys):
        writer.writerow([key, "identical", result.env_a[key], result.env_b[key]])

    return output.getvalue()


def _export_json(result: EnvDiffResult, label_a: str, label_b: str) -> str:
    data = {
        "labels": {"a": label_a, "b": label_b},
        "only_in_a": {k: result.env_a[k] for k in sorted(result.only_in_a)},
        "only_in_b": {k: result.env_b[k] for k in sorted(result.only_in_b)},
        "value_differs": {
            k: {label_a: result.env_a[k], label_b: result.env_b[k]}
            for k in sorted(result.value_differs)
        },
        "identical": {k: result.env_a[k] for k in sorted(result.common_keys)},
    }
    return json.dumps(data, indent=2)


def _export_dotenv(result: EnvDiffResult) -> str:
    """Export a merged .env using env_a values, annotating conflicts."""
    lines = []
    all_keys = sorted(result.env_a.keys() | result.env_b.keys())
    for key in all_keys:
        if key in result.value_differs:
            lines.append(f"# CONFLICT: {key}")
            lines.append(f"# env_a: {key}={result.env_a[key]}")
            lines.append(f"# env_b: {key}={result.env_b[key]}")
            lines.append(f"{key}={result.env_a[key]}")
        elif key in result.env_a:
            lines.append(f"{key}={result.env_a[key]}")
        else:
            lines.append(f"# only_in_b: {key}={result.env_b[key]}")
    return "\n".join(lines) + "\n"


def export(
    result: EnvDiffResult,
    fmt: ExportFormat,
    output_path: Optional[Path] = None,
    label_a: str = "a",
    label_b: str = "b",
) -> str:
    """Export diff result to the given format. Optionally write to a file."""
    if fmt == ExportFormat.CSV:
        content = _export_csv(result, label_a, label_b)
    elif fmt == ExportFormat.JSON:
        content = _export_json(result, label_a, label_b)
    elif fmt == ExportFormat.DOTENV:
        content = _export_dotenv(result)
    else:
        raise ValueError(f"Unsupported export format: {fmt}")

    if output_path is not None:
        Path(output_path).write_text(content, encoding="utf-8")

    return content
