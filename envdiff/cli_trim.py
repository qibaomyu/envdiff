"""CLI sub-command: trim — remove empty, whitespace-only, or placeholder keys."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envdiff.loader import load_env_file
from envdiff.trimmer import trim_env


def add_trim_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("env_file", help="Path to the .env file to trim")
    parser.add_argument(
        "--keep-empty",
        action="store_true",
        default=False,
        help="Do not remove keys with empty values",
    )
    parser.add_argument(
        "--keep-whitespace",
        action="store_true",
        default=False,
        help="Do not remove keys with whitespace-only values",
    )
    parser.add_argument(
        "--keep-placeholders",
        action="store_true",
        default=False,
        help="Do not remove keys with placeholder values",
    )
    parser.add_argument(
        "--extra-pattern",
        dest="extra_patterns",
        metavar="PATTERN",
        action="append",
        default=[],
        help="Additional regex pattern to treat as a placeholder (repeatable)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "dotenv"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--show-removed",
        action="store_true",
        default=False,
        help="Also list removed keys and reasons",
    )


def run_trim(args: argparse.Namespace) -> int:
    env = load_env_file(args.env_file)
    result = trim_env(
        env,
        remove_empty=not args.keep_empty,
        remove_whitespace_only=not args.keep_whitespace,
        remove_placeholders=not args.keep_placeholders,
        extra_placeholder_patterns=args.extra_patterns or None,
    )

    fmt = args.format

    if fmt == "json":
        out = {
            "summary": result.summary(),
            "trimmed": result.trimmed,
        }
        if args.show_removed:
            out["removed"] = [
                {"key": e.key, "value": e.value, "reason": e.reason}
                for e in result.removed
            ]
        print(json.dumps(out, indent=2))
    elif fmt == "dotenv":
        for key, value in result.trimmed.items():
            print(f"{key}={value}")
    else:
        print(result.summary())
        if args.show_removed and result.removed:
            print("\nRemoved keys:")
            for entry in result.removed:
                print(f"  {entry.key!r:30s}  [{entry.reason}]")

    return 1 if result.has_removals() else 0
