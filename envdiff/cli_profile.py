"""CLI subcommand for profiling an environment file."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from envdiff.loader import load_env_file, load_from_os_environ
from envdiff.profiler import profile_env


def add_profile_args(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "profile",
        help="Profile and categorize environment variables from a file or the current OS environment.",
    )
    parser.add_argument(
        "env_file",
        nargs="?",
        default=None,
        help="Path to .env file. Omit to use the current OS environment.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--category",
        default=None,
        metavar="CATEGORY",
        help="Filter output to a specific category.",
    )
    parser.set_defaults(func=run_profile)


def run_profile(args: argparse.Namespace) -> int:
    if args.env_file:
        try:
            env = load_env_file(args.env_file)
        except FileNotFoundError:
            print(f"Error: file not found: {args.env_file}", file=sys.stderr)
            return 2
    else:
        env = load_from_os_environ()

    profile = profile_env(env)

    category_filter: Optional[str] = args.category

    if args.format == "json":
        entries = [
            {
                "key": e.key,
                "category": e.category,
                "is_empty": e.is_empty,
                "length": e.length,
            }
            for e in profile.entries
            if category_filter is None or e.category == category_filter
        ]
        output = {
            "total": profile.total,
            "empty_count": profile.empty_count,
            "categories": profile.categories,
            "entries": entries,
        }
        print(json.dumps(output, indent=2))
    else:
        if category_filter:
            filtered = [e for e in profile.entries if e.category == category_filter]
            print(f"Category: {category_filter} ({len(filtered)} keys)")
            for e in filtered:
                empty_marker = "  [EMPTY]" if e.is_empty else ""
                print(f"  {e.key}{empty_marker}")
        else:
            print(profile.summary())

    return 0
