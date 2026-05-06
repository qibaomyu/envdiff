"""CLI subcommand: lint — check env files for style and convention issues."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.loader import load_env_file
from envdiff.linter import lint_env, LintIssue


def add_lint_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "lint",
        help="Lint an env file for style and convention issues.",
    )
    parser.add_argument("file", help="Path to the .env file to lint.")
    parser.add_argument(
        "--allow-lowercase",
        action="store_true",
        default=False,
        help="Allow lowercase letters in keys without warning.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with non-zero code if any warnings exist (not just errors).",
    )
    parser.set_defaults(func=run_lint)


def run_lint(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2

    result = lint_env(env, allow_lowercase=args.allow_lowercase)

    if not result.has_issues():
        print(f"OK — no issues found in {args.file}")
        return 0

    _print_issues(result.errors(), "ERROR")
    _print_issues(result.warnings(), "WARNING")
    print(f"\n{result.summary()}")

    if result.errors():
        return 1
    if args.strict and result.warnings():
        return 1
    return 0


def _print_issues(issues: List[LintIssue], label: str) -> None:
    for issue in issues:
        print(f"  [{label}] [{issue.code}] {issue.key}: {issue.message}")
