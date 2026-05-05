"""CLI helpers for the --export flag in envdiff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from envdiff.comparator import compare_envs
from envdiff.exporter import ExportFormat, export
from envdiff.loader import load_env_file


def add_export_args(parser: argparse.ArgumentParser) -> None:
    """Attach export-related arguments to an existing ArgumentParser."""
    parser.add_argument(
        "--export-format",
        choices=[f.value for f in ExportFormat],
        default=None,
        help="Export diff result to a file in the specified format.",
    )
    parser.add_argument(
        "--export-output",
        metavar="FILE",
        default=None,
        help="Destination file path for the exported result.",
    )


def run_export(
    file_a: str,
    file_b: str,
    fmt_str: str,
    output_path: Optional[str],
    label_a: str = "a",
    label_b: str = "b",
) -> int:
    """Load two env files, compare them, and export to the given format.

    Returns 0 on success, 1 on error.
    """
    try:
        env_a = load_env_file(file_a)
        env_b = load_env_file(file_b)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = compare_envs(env_a, env_b)

    try:
        fmt = ExportFormat(fmt_str)
    except ValueError:
        print(f"Error: unsupported export format '{fmt_str}'", file=sys.stderr)
        return 1

    out_path = Path(output_path) if output_path else None
    content = export(result, fmt, output_path=out_path, label_a=label_a, label_b=label_b)

    if out_path is None:
        print(content, end="")
    else:
        print(f"Exported to {out_path}")

    return 0
