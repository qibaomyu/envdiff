"""CLI sub-command: scope — extract a named prefix-scope from an env file."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.loader import load_env_file
from envdiff.scoper import list_scopes, scope_env


def add_scope_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "scope",
        help="Extract or list prefix-scopes from an env file.",
    )
    p.add_argument("env_file", help="Path to the .env file.")
    p.add_argument(
        "--scope",
        metavar="NAME",
        help="Scope prefix to extract (e.g. DB).  Omit to list all scopes.",
    )
    p.add_argument(
        "--separator",
        default="_",
        metavar="SEP",
        help="Key separator character (default: '_').",
    )
    p.add_argument(
        "--no-strip",
        action="store_true",
        default=False,
        help="Keep the scope prefix in the output keys.",
    )
    p.add_argument(
        "--min-keys",
        type=int,
        default=1,
        metavar="N",
        help="Minimum keys required to list a scope (default: 1).",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    p.set_defaults(func=run_scope)


def run_scope(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    if args.scope is None:
        # List mode
        scopes: List[str] = list_scopes(
            env, separator=args.separator, min_keys=args.min_keys
        )
        if args.output_format == "json":
            print(json.dumps({"scopes": scopes}, indent=2))
        else:
            if scopes:
                for s in scopes:
                    print(s)
            else:
                print("(no scopes found)")
        return 0

    # Extract mode
    result = scope_env(
        env,
        scope=args.scope,
        separator=args.separator,
        strip_prefix=not args.no_strip,
    )

    if args.output_format == "json":
        print(json.dumps({"scope": result.scope, "env": result.stripped}, indent=2))
    else:
        if not result.stripped:
            print(f"(no keys found for scope '{result.scope}')")
        else:
            width = max(len(k) for k in result.stripped)
            for key, value in sorted(result.stripped.items()):
                print(f"{key:<{width}} = {value}")

    return 0
