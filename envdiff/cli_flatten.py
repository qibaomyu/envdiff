"""CLI sub-command: flatten JSON-valued env keys into dot-separated keys."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.flattener import flatten_env
from envdiff.loader import load_env_file


def add_flatten_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "flatten",
        help="Expand JSON-object values into dot-separated keys.",
    )
    parser.add_argument("env_file", help="Path to the .env file to flatten.")
    parser.add_argument(
        "--separator",
        default=".",
        metavar="SEP",
        help="Separator used between key segments (default: '.').",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--show-skipped",
        action="store_true",
        default=False,
        help="Also list keys that were not expanded.",
    )
    parser.set_defaults(func=run_flatten)


def run_flatten(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    result = flatten_env(env, separator=args.separator)

    if args.output_format == "json":
        payload = {
            "flattened": result.as_env(),
            "skipped": result.skipped,
            "summary": result.summary(),
        }
        print(json.dumps(payload, indent=2))
        return 0

    # --- text output ---
    flat_env = result.as_env()
    if not flat_env:
        print("(no keys)")
        return 0

    for key, value in sorted(flat_env.items()):
        print(f"{key}={value}")

    if args.show_skipped and result.skipped:
        print()
        print("Skipped (not a JSON object):")
        for k in sorted(result.skipped):
            print(f"  {k}")

    print()
    print(result.summary())
    return 0
