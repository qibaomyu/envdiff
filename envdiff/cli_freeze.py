"""CLI sub-commands for the freeze feature."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.freezer import check_freeze, freeze_env, load_freeze
from envdiff.loader import load_env_file


def add_freeze_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("freeze", help="Freeze or verify a locked env snapshot.")
    sub = p.add_subparsers(dest="freeze_cmd", required=True)

    # freeze save
    save_p = sub.add_parser("save", help="Save a freeze file from an env file.")
    save_p.add_argument("env_file", help="Source .env file.")
    save_p.add_argument("freeze_file", help="Destination freeze file path.")
    save_p.add_argument("--label", default="", help="Optional label for the freeze.")
    save_p.add_argument(
        "--keys", nargs="*", metavar="KEY", help="Specific keys to freeze (default: all)."
    )

    # freeze check
    check_p = sub.add_parser("check", help="Check an env file against a freeze file.")
    check_p.add_argument("freeze_file", help="Freeze file to compare against.")
    check_p.add_argument("env_file", help="Env file to validate.")
    check_p.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero even when there are no violations (dry-run mode).",
    )


def _run_save(args: argparse.Namespace) -> int:
    env = load_env_file(args.env_file)
    if args.keys:
        env = {k: v for k, v in env.items() if k in args.keys}
    freeze_env(env, args.freeze_file, label=args.label)
    print(f"Frozen {len(env)} key(s) to {args.freeze_file!r}.")
    return 0


def _run_check(args: argparse.Namespace) -> int:
    try:
        frozen = load_freeze(args.freeze_file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error loading freeze file: {exc}", file=sys.stderr)
        return 2

    actual = load_env_file(args.env_file)
    result = check_freeze(frozen=frozen, actual=actual)
    print(result.summary())
    if result.has_violations():
        return 1
    return 0


def run_freeze(args: argparse.Namespace) -> int:
    if args.freeze_cmd == "save":
        return _run_save(args)
    if args.freeze_cmd == "check":
        return _run_check(args)
    print(f"Unknown freeze sub-command: {args.freeze_cmd}", file=sys.stderr)
    return 2
