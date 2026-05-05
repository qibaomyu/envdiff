"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.comparator import compare_envs
from envdiff.filter import filter_keys, filter_keys_by_prefix, filter_keys_by_regex
from envdiff.loader import load_env_file, load_from_os_environ
from envdiff.reporter import OutputFormat, render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare environment variable configurations across deployment targets.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Paths to .env files to compare (use '-' to read from OS environ).",
    )
    parser.add_argument(
        "--format",
        choices=[f.value for f in OutputFormat],
        default=OutputFormat.TEXT.value,
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--label",
        action="append",
        dest="labels",
        metavar="LABEL",
        help="Custom label for each file (repeatable, must match number of files).",
    )
    parser.add_argument(
        "--include",
        action="append",
        dest="include_patterns",
        metavar="PATTERN",
        help="Glob pattern: only compare matching keys (repeatable).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        dest="exclude_patterns",
        metavar="PATTERN",
        help="Glob pattern: skip matching keys (repeatable).",
    )
    parser.add_argument(
        "--prefix",
        metavar="PREFIX",
        help="Only compare keys starting with PREFIX.",
    )
    parser.add_argument(
        "--regex",
        metavar="PATTERN",
        help="Only compare keys matching this regular expression.",
    )
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if len(args.files) < 2:
        parser.error("At least two files (or '-') are required.")

    labels = args.labels or args.files
    if len(labels) != len(args.files):
        parser.error("Number of --label options must match number of files.")

    envs = {}
    for label, path in zip(labels, args.files):
        if path == "-":
            env = load_from_os_environ()
        else:
            env = load_env_file(path)

        if args.prefix:
            env = filter_keys_by_prefix(env, args.prefix)
        if args.regex:
            env = filter_keys_by_regex(env, args.regex)
        if args.include_patterns or args.exclude_patterns:
            env = filter_keys(
                env,
                include_patterns=args.include_patterns,
                exclude_patterns=args.exclude_patterns,
            )

        envs[label] = env

    result = compare_envs(envs)
    fmt = OutputFormat(args.format)
    print(render(result, fmt))
    return 1 if result.has_differences() else 0


def main() -> None:  # pragma: no cover
    sys.exit(run())
