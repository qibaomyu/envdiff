"""CLI sub-command: mask — display env file with sensitive values masked."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.loader import load_env_file
from envdiff.masker import mask_env, mask_summary
from envdiff.redactor import is_sensitive


def add_mask_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "mask",
        help="Display env file with sensitive values masked.",
    )
    p.add_argument("envfile", help="Path to the .env file to mask.")
    p.add_argument(
        "--keys",
        nargs="*",
        metavar="KEY",
        default=None,
        help="Explicit keys to mask. Defaults to auto-detected sensitive keys.",
    )
    p.add_argument(
        "--partial",
        action="store_true",
        help="Reveal the last 4 characters of each masked value.",
    )
    p.add_argument(
        "--mask",
        default="***",
        help="Replacement string used for masking (default: ***).",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary line after the masked output.",
    )
    p.set_defaults(func=run_mask)


def run_mask(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.envfile)
    except FileNotFoundError:
        print(f"error: file not found: {args.envfile}", file=sys.stderr)
        return 1

    if args.keys is not None:
        keys_to_mask: List[str] = args.keys
    else:
        keys_to_mask = [k for k in env if is_sensitive(k)]

    results = mask_env(env, keys_to_mask, mask=args.mask, partial=args.partial)

    for key, result in results.items():
        print(f"{key}={result.masked_value}")

    if args.summary:
        print()
        print(mask_summary(results))

    return 0
