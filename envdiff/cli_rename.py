"""CLI sub-command: rename keys in an env file."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.loader import load_env_file
from envdiff.renamer import rename_keys
from envdiff.exporter import export, ExportFormat


def add_rename_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("env_file", help="Path to the .env file to process")
    parser.add_argument(
        "--rename",
        metavar="OLD=NEW",
        action="append",
        default=[],
        dest="renames",
        help="Rename rule in OLD=NEW format (repeatable)",
    )
    parser.add_argument(
        "--mapping",
        metavar="FILE",
        help="JSON file containing {old: new} rename mapping",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Allow overwriting an existing target key",
    )
    parser.add_argument(
        "--keep-original",
        action="store_true",
        default=False,
        help="Retain the original key alongside the renamed one",
    )
    parser.add_argument(
        "--format",
        choices=["text", "dotenv", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress summary output",
    )


def _parse_renames(rules: List[str]) -> dict:
    mapping = {}
    for rule in rules:
        if "=" not in rule:
            raise argparse.ArgumentTypeError(f"Invalid rename rule (expected OLD=NEW): {rule!r}")
        old, new = rule.split("=", 1)
        mapping[old.strip()] = new.strip()
    return mapping


def run_rename(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    mapping = _parse_renames(args.renames)

    if args.mapping:
        try:
            with open(args.mapping) as fh:
                file_mapping = json.load(fh)
            mapping.update(file_mapping)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error loading mapping file: {exc}", file=sys.stderr)
            return 1

    if not mapping:
        print("error: no rename rules provided (use --rename or --mapping)", file=sys.stderr)
        return 1

    result = rename_keys(env, mapping, overwrite=args.overwrite, keep_original=args.keep_original)

    fmt = args.format
    if fmt == "dotenv":
        for k, v in result.env.items():
            print(f"{k}={v}")
    elif fmt == "json":
        print(json.dumps(result.env, indent=2))
    else:
        for entry in result.renamed():
            print(f"  renamed : {entry.old_key} -> {entry.new_key}")
        for entry in result.skipped():
            print(f"  skipped : {entry.old_key} -> {entry.new_key}  ({entry.skip_reason})")

    if not args.quiet:
        print(result.summary())

    return 1 if result.skipped() else 0
