"""CLI sub-command: dedup — find duplicate values in an env file."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envdiff.deduplicator import find_duplicates
from envdiff.loader import load_env_file


def add_dedup_args(parser: argparse.ArgumentParser) -> None:
    """Register *dedup* arguments onto *parser*."""
    parser.add_argument(
        "envfile",
        help="Path to the .env file to scan for duplicate values.",
    )
    parser.add_argument(
        "--include-empty",
        action="store_true",
        default=False,
        help="Treat empty string as a value that can be duplicated.",
    )
    parser.add_argument(
        "--ignore-key",
        metavar="KEY",
        action="append",
        dest="ignore_keys",
        default=[],
        help="Exclude KEY from the scan (repeatable).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when duplicates are found.",
    )


def run_dedup(
    args: argparse.Namespace,
    out=sys.stdout,
    err=sys.stderr,
) -> int:
    """Execute the dedup command.  Returns the process exit code."""
    try:
        env = load_env_file(args.envfile)
    except FileNotFoundError:
        err.write(f"Error: file not found: {args.envfile}\n")
        return 2

    result = find_duplicates(
        env,
        ignore_empty=not args.include_empty,
        ignore_keys=args.ignore_keys or [],
    )

    if args.output_format == "json":
        payload = [
            {"value": g.value, "keys": sorted(g.keys)}
            for g in result.groups
        ]
        out.write(json.dumps(payload, indent=2))
        out.write("\n")
    else:
        out.write(result.summary())
        out.write("\n")

    if args.exit_code and result.has_duplicates:
        return 1
    return 0
