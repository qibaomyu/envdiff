"""CLI sub-command: pin — check an env file against a pinned reference."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.loader import load_env_file
from envdiff.pinner import pin_env, PinResult


def add_pin_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "pin",
        help="Check an env file against a pinned reference and report drift.",
    )
    parser.add_argument("pinned", help="Reference (pinned) .env file.")
    parser.add_argument("actual", help="Actual .env file to validate.")
    parser.add_argument(
        "--no-extra",
        dest="no_extra",
        action="store_true",
        default=False,
        help="Treat keys in ACTUAL that are absent from PINNED as violations.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_pin)


def _render_text(result: PinResult) -> str:
    return result.summary()


def _render_json(result: PinResult) -> str:
    data = {
        "has_violations": result.has_violations(),
        "pinned_keys": result.pinned_keys,
        "violations": [
            {
                "key": v.key,
                "reason": v.reason,
                "pinned_value": v.pinned_value,
                "actual_value": v.actual_value,
            }
            for v in result.violations
        ],
    }
    return json.dumps(data, indent=2)


def run_pin(args: argparse.Namespace) -> int:
    """Execute the pin sub-command.  Returns an exit code."""
    try:
        pinned_env = load_env_file(args.pinned)
    except FileNotFoundError:
        print(f"error: pinned file not found: {args.pinned}", file=sys.stderr)
        return 2

    try:
        actual_env = load_env_file(args.actual)
    except FileNotFoundError:
        print(f"error: actual file not found: {args.actual}", file=sys.stderr)
        return 2

    result = pin_env(pinned_env, actual_env, allow_extra=not args.no_extra)

    if args.format == "json":
        print(_render_json(result))
    else:
        print(_render_text(result))

    return 1 if result.has_violations() else 0
