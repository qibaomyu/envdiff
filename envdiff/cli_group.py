"""CLI sub-command: envdiff group — display grouped env vars."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.grouper import group_by_prefix, group_by_regex
from envdiff.loader import load_env_file


def add_group_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "group",
        help="Group environment variables by prefix or regex pattern.",
    )
    p.add_argument("envfile", help="Path to the .env file to group.")
    p.add_argument(
        "--by",
        choices=["prefix", "regex"],
        default="prefix",
        help="Grouping strategy (default: prefix).",
    )
    p.add_argument(
        "--separator",
        default="_",
        help="Separator used for prefix splitting (default: '_').",
    )
    p.add_argument(
        "--min-group-size",
        type=int,
        default=1,
        metavar="N",
        help="Minimum keys for a prefix group; smaller groups become ungrouped.",
    )
    p.add_argument(
        "--pattern",
        action="append",
        dest="patterns",
        metavar="NAME=REGEX",
        help="Named regex pattern (repeatable). Example: db=^DB_",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    p.set_defaults(func=run_group)


def _parse_patterns(raw: List[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in raw or []:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                f"Pattern must be NAME=REGEX, got: {item!r}"
            )
        name, _, regex = item.partition("=")
        result[name.strip()] = regex.strip()
    return result


def run_group(args: argparse.Namespace) -> int:
    env = load_env_file(args.envfile)

    if args.by == "prefix":
        groups = group_by_prefix(
            env,
            separator=args.separator,
            min_group_size=args.min_group_size,
        )
    else:
        patterns = _parse_patterns(args.patterns or [])
        groups = group_by_regex(env, patterns)

    if args.output_format == "json":
        data = {name: g.keys for name, g in sorted(groups.items())}
        print(json.dumps(data, indent=2))
    else:
        for name, group in sorted(groups.items()):
            print(f"[{name}]  ({len(group)} keys)")
            for key in group.keys:
                print(f"  {key}")

    return 0
