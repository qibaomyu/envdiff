"""CLI subcommand: diff two snapshots or env files and show a changelog."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from envdiff.differ import diff_snapshots, format_changelog
from envdiff.loader import load_env_file
from envdiff.snapshot import load_snapshot


def add_diff_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "diff",
        help="Compare two env files or snapshots and show a changelog.",
    )
    parser.add_argument("before", help="Path to the 'before' env file or snapshot (.json).")
    parser.add_argument("after", help="Path to the 'after' env file or snapshot (.json).")
    parser.add_argument(
        "--include-unchanged",
        action="store_true",
        default=False,
        help="Also list keys whose values did not change.",
    )
    parser.add_argument(
        "--label-before",
        default=None,
        help="Label for the 'before' source (default: filename).",
    )
    parser.add_argument(
        "--label-after",
        default=None,
        help="Label for the 'after' source (default: filename).",
    )
    parser.set_defaults(func=run_diff)


def _load_source(path: str) -> dict:
    """Load env vars from either a .json snapshot or a plain .env file."""
    if path.endswith(".json"):
        return load_snapshot(path)
    return load_env_file(path)


def run_diff(args: argparse.Namespace) -> int:
    """Execute the diff subcommand. Returns exit code."""
    try:
        before = _load_source(args.before)
        after = _load_source(args.after)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    changelog = diff_snapshots(
        before,
        after,
        include_unchanged=args.include_unchanged,
    )

    label_before: str = args.label_before or args.before
    label_after: str = args.label_after or args.after

    print(format_changelog(changelog, label_before=label_before, label_after=label_after))
    return 1 if changelog.has_changes else 0
