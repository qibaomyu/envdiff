"""CLI sub-command: sort — display env vars sorted by a chosen criterion."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from envdiff.loader import load_env_file
from envdiff.sorter import SortBy, SortOrder, rank_by_value_length, sort_env


def add_sort_args(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "sort",
        help="Sort environment variables by key, value, or value length.",
    )
    parser.add_argument("file", help="Path to the .env file to sort.")
    parser.add_argument(
        "--by",
        choices=[s.value for s in SortBy],
        default=SortBy.KEY.value,
        help="Sort criterion (default: key).",
    )
    parser.add_argument(
        "--order",
        choices=[o.value for o in SortOrder],
        default=SortOrder.ASC.value,
        help="Sort order (default: asc).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="Show only the top N entries by value length.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_sort)


def run_sort(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    try:
        env = load_env_file(args.file)
    except FileNotFoundError:
        err.write(f"Error: file not found: {args.file}\n")
        return 1

    if args.top is not None:
        entries = rank_by_value_length(env, top_n=args.top)
    else:
        sort_by = SortBy(args.by)
        order = SortOrder(args.order)
        result = sort_env(env, sort_by=sort_by, order=order)
        entries = result.entries

    if args.output_format == "json":
        out.write(json.dumps(dict(entries), indent=2))
        out.write("\n")
    else:
        for key, value in entries:
            out.write(f"{key}={value}\n")

    return 0
