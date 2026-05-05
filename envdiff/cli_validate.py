"""CLI sub-command for validating environment files."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.loader import load_env_file
from envdiff.validator import validate_env


def add_validate_args(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "validate",
        help="Validate an environment file against a set of rules.",
    )
    parser.add_argument("env_file", help="Path to the .env file to validate.")
    parser.add_argument(
        "--require",
        metavar="KEY",
        nargs="+",
        default=[],
        help="Keys that must be present.",
    )
    parser.add_argument(
        "--forbid",
        metavar="KEY",
        nargs="+",
        default=[],
        help="Keys that must not be present.",
    )
    parser.add_argument(
        "--no-empty",
        action="store_true",
        default=False,
        help="Warn when keys have empty values.",
    )


def run_validate(args: argparse.Namespace) -> int:
    """Run the validate sub-command. Returns exit code."""
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2

    result = validate_env(
        env,
        required_keys=args.require or None,
        forbidden_keys=args.forbid or None,
        no_empty_values=args.no_empty,
    )

    if not result.issues:
        print(f"OK — no issues found in {args.env_file}")
        return 0

    for issue in result.issues:
        prefix = "ERROR" if issue.severity == "error" else "WARN "
        print(f"[{prefix}] {issue.key}: {issue.message}")

    if result.has_errors:
        return 1
    return 0
