"""CLI sub-command: split an env file into named buckets."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Tuple

from envdiff.loader import load_env_file
from envdiff.splitter import split_env


def add_split_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("env_file", help="Path to the .env file to split")
    parser.add_argument(
        "--rule",
        dest="rules",
        metavar="NAME:PATTERN",
        action="append",
        default=[],
        help="Bucket rule in NAME:PATTERN format (repeatable)",
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        default=False,
        help="Treat patterns as regular expressions instead of prefixes",
    )
    parser.add_argument(
        "--no-remainder",
        dest="no_remainder",
        action="store_true",
        default=False,
        help="Discard keys that do not match any rule",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )


def _parse_rules(raw: List[str]) -> List[Tuple[str, str]]:
    rules: List[Tuple[str, str]] = []
    for item in raw:
        if ":" not in item:
            raise argparse.ArgumentTypeError(
                f"Rule {item!r} must be in NAME:PATTERN format"
            )
        name, _, pattern = item.partition(":")
        rules.append((name.strip(), pattern.strip()))
    return rules


def run_split(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    try:
        rules = _parse_rules(args.rules)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = split_env(
        env,
        rules,
        use_regex=args.regex,
        keep_remainder=not args.no_remainder,
    )

    if args.format == "json":
        payload = {
            name: dict(bucket.env)
            for name, bucket in result.buckets.items()
        }
        if not args.no_remainder:
            payload["remainder"] = result.remainder
        print(json.dumps(payload, indent=2))
    else:
        for name, bucket in result.buckets.items():
            print(f"[{name}]  ({len(bucket)} key(s))")
            for k, v in bucket.env.items():
                print(f"  {k}={v}")
        if not args.no_remainder:
            print(f"[remainder]  ({len(result.remainder)} key(s))")
            for k, v in result.remainder.items():
                print(f"  {k}={v}")

    return 0
