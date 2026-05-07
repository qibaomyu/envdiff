"""CLI sub-command: tag — tag env variables by pattern rules."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.loader import load_env_file
from envdiff.tagger import tag_env


def add_tag_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("env_file", help="Path to the .env file to tag.")
    parser.add_argument(
        "--rule",
        dest="rules",
        metavar="PATTERN=TAG[,TAG]",
        action="append",
        default=[],
        help=(
            "Tagging rule in the form REGEX=tag1,tag2. "
            "May be supplied multiple times."
        ),
    )
    parser.add_argument(
        "--default-tag",
        dest="default_tags",
        metavar="TAG",
        action="append",
        default=[],
        help="Tag to apply to keys that match no rule.",
    )
    parser.add_argument(
        "--filter-tag",
        dest="filter_tag",
        default=None,
        help="Only display entries that carry this tag.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )


def _parse_rules(raw: List[str]) -> dict:
    rules: dict = {}
    for item in raw:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                f"Invalid rule {item!r}: expected PATTERN=TAG[,TAG]"
            )
        pattern, tag_str = item.split("=", 1)
        rules[pattern] = [t.strip() for t in tag_str.split(",") if t.strip()]
    return rules


def run_tag(args: argparse.Namespace) -> int:
    env = load_env_file(args.env_file)
    rules = _parse_rules(args.rules)
    default_tags = args.default_tags or None
    tagged = tag_env(env, rules, default_tags=default_tags)

    entries = (
        tagged.by_tag(args.filter_tag)
        if args.filter_tag
        else tagged.entries
    )

    if args.format == "json":
        data = [
            {"key": e.key, "value": e.value, "tags": e.tags}
            for e in entries
        ]
        print(json.dumps(data, indent=2))
    else:
        if not entries:
            print("No entries to display.")
        else:
            for entry in entries:
                tag_str = ", ".join(entry.tags) if entry.tags else "(none)"
                print(f"{entry.key}  [{tag_str}]")

    return 0
