"""CLI sub-command: transform env file values."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envdiff.loader import load_env_file
from envdiff.transformer import BUILT_IN_RULES, transform_env
from envdiff.exporter import _export_dotenv


def add_transform_args(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "transform",
        help="Apply transformation rules to env variable values.",
    )
    p.add_argument("env_file", help="Path to the .env file to transform.")
    p.add_argument(
        "--rules",
        nargs="+",
        default=["strip"],
        metavar="RULE",
        help=(
            f"One or more rules to apply in order. "
            f"Built-in: {', '.join(sorted(BUILT_IN_RULES))}. Default: strip."
        ),
    )
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        default=None,
        help="Limit transformation to these keys only.",
    )
    p.add_argument(
        "--format",
        choices=["text", "dotenv", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--only-changed",
        action="store_true",
        default=False,
        help="Only show/output keys whose values changed.",
    )
    p.set_defaults(func=run_transform)


def run_transform(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    try:
        result = transform_env(env, rules=args.rules, keys=args.keys)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    entries = result.changed() if args.only_changed else result.entries
    filtered_env = {e.key: e.transformed for e in entries if e.rule_applied != "skipped"}

    fmt = args.format
    if fmt == "json":
        print(json.dumps(filtered_env, indent=2))
    elif fmt == "dotenv":
        print(_export_dotenv({"env": filtered_env}).strip())
    else:
        print(f"# {result.summary()}")
        for entry in entries:
            if entry.rule_applied == "skipped":
                continue
            marker = "*" if entry.original != entry.transformed else " "
            print(f"{marker} {entry.key}={entry.transformed!r}")

    return 0
