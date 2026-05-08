"""CLI sub-command: diff-summary — show a compact summary of changes between two env sources."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.cli_diff import _load_source
from envdiff.differ import diff_envs
from envdiff.differ_summary import summarize_diff, text_diff_summary


def add_diff_summary_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "diff-summary",
        help="Show a compact summary of changes between two env sources.",
    )
    parser.add_argument("before", help="Before env file or snapshot path.")
    parser.add_argument("after", help="After env file or snapshot path.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when changes are detected.",
    )
    parser.set_defaults(func=run_diff_summary)


def run_diff_summary(args: argparse.Namespace) -> int:
    before_env = _load_source(args.before)
    after_env = _load_source(args.after)

    changelog = diff_envs(before_env, after_env)
    summary = summarize_diff(changelog)

    if args.fmt == "json":
        output = {
            "total": summary.total,
            "added": summary.added,
            "removed": summary.removed,
            "modified": summary.modified,
            "unchanged": summary.unchanged,
        }
        print(json.dumps(output, indent=2))
    else:
        print(text_diff_summary(summary))

    if args.exit_code and changelog.has_changes():
        return 1
    return 0
