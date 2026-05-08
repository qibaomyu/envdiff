"""CLI sub-command: annotate — attach comments to env keys."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.annotator import annotate_env, render_annotated_dotenv
from envdiff.loader import load_env_file


def add_annotate_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "annotate",
        help="Attach inline comments to environment variables.",
    )
    p.add_argument("env_file", help="Path to the .env file to annotate.")
    p.add_argument(
        "--rule",
        metavar="KEY=COMMENT",
        action="append",
        dest="rules",
        default=[],
        help="Annotation rule in KEY=COMMENT format. Repeatable.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json", "dotenv"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )


def _parse_rules(raw: List[str]) -> dict:
    rules: dict = {}
    for item in raw:
        if "=" not in item:
            print(f"[warn] Skipping invalid rule (no '='): {item!r}", file=sys.stderr)
            continue
        key, _, comment = item.partition("=")
        rules[key.strip()] = comment.strip()
    return rules


def run_annotate(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"[error] File not found: {args.env_file}", file=sys.stderr)
        return 1

    rules = _parse_rules(args.rules)
    result = annotate_env(env, rules)

    fmt = args.output_format

    if fmt == "dotenv":
        print(render_annotated_dotenv(result))
    elif fmt == "json":
        data = {
            "annotated": [
                {"key": e.key, "value": e.value, "comment": e.comment}
                for e in result.entries
            ],
            "unannotated": result.unannotated,
        }
        print(json.dumps(data, indent=2))
    else:  # text
        print(result.summary())
        for entry in result.entries:
            print(f"  {entry.key}  # {entry.comment}")
        if result.unannotated:
            print("Unannotated:")
            for key in result.unannotated:
                print(f"  {key}")

    return 0
