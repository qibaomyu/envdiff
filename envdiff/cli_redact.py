"""CLI sub-command: redact — print an env file with sensitive values masked."""

import argparse
import sys
from typing import List, Optional

from envdiff.loader import load_env_file
from envdiff.redactor import redact_env, REDACT_PLACEHOLDER


def add_redact_args(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "redact",
        help="Print an env file with sensitive values replaced by a placeholder.",
    )
    parser.add_argument("env_file", help="Path to the .env file to redact.")
    parser.add_argument(
        "--pattern",
        dest="patterns",
        metavar="REGEX",
        action="append",
        default=None,
        help="Additional regex pattern for sensitive key names (can be repeated).",
    )
    parser.add_argument(
        "--placeholder",
        default=REDACT_PLACEHOLDER,
        help="Replacement string for redacted values (default: %(default)s).",
    )
    parser.add_argument(
        "--format",
        choices=["dotenv", "plain"],
        default="dotenv",
        dest="fmt",
        help="Output format (default: dotenv).",
    )
    parser.set_defaults(func=run_redact)


def run_redact(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    redacted = redact_env(env, patterns=args.patterns, placeholder=args.placeholder)

    if args.fmt == "dotenv":
        for key, value in redacted.items():
            print(f"{key}={value}")
    else:
        for key, value in redacted.items():
            print(f"{key}: {value}")

    return 0
