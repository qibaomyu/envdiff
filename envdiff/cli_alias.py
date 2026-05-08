"""CLI sub-command: alias — apply human-friendly aliases to env keys."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict

from envdiff.aliaser import alias_env
from envdiff.loader import load_env_file


def add_alias_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--alias",
        metavar="ORIGINAL=ALIAS",
        action="append",
        dest="alias_pairs",
        default=[],
        help="Map ORIGINAL key to ALIAS name (repeatable)",
    )
    parser.add_argument(
        "--no-unaliased",
        action="store_true",
        default=False,
        help="Omit keys that have no alias mapping from output",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "dotenv"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with non-zero status when any alias key is missing from the env",
    )


def _parse_alias_pairs(pairs: list) -> Dict[str, str]:
    aliases: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"Invalid alias pair {pair!r}: expected ORIGINAL=ALIAS"
            )
        original, _, alias = pair.partition("=")
        aliases[original.strip()] = alias.strip()
    return aliases


def run_alias(args: argparse.Namespace) -> int:
    env = load_env_file(args.env_file)
    aliases = _parse_alias_pairs(args.alias_pairs)
    result = alias_env(env, aliases, include_unaliased=not args.no_unaliased)

    fmt = args.format

    if fmt == "json":
        payload = {
            "aliased": result.by_alias(),
            "unaliased": result.unaliased,
            "missing_keys": result.missing_keys,
        }
        print(json.dumps(payload, indent=2))
    elif fmt == "dotenv":
        for entry in result.entries:
            print(f"{entry.alias}={entry.value}")
        if not args.no_unaliased:
            for k, v in result.unaliased.items():
                print(f"{k}={v}")
    else:  # text
        print(result.summary())

    if args.strict and result.missing_keys:
        return 1
    return 0
