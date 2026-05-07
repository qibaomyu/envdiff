"""CLI sub-command: patch — apply patch operations to an env file."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.loader import load_env_file
from envdiff.patcher import PatchInstruction, apply_patch


def add_patch_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "patch",
        help="Apply set/unset/rename operations to an env file.",
    )
    p.add_argument("env_file", help="Path to the .env file to patch.")
    p.add_argument(
        "--set",
        metavar="KEY=VALUE",
        action="append",
        default=[],
        dest="sets",
        help="Set KEY to VALUE (repeatable).",
    )
    p.add_argument(
        "--unset",
        metavar="KEY",
        action="append",
        default=[],
        dest="unsets",
        help="Remove KEY from the env (repeatable).",
    )
    p.add_argument(
        "--rename",
        metavar="OLD=NEW",
        action="append",
        default=[],
        dest="renames",
        help="Rename OLD key to NEW key (repeatable).",
    )
    p.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Skip set operations that would overwrite an existing key.",
    )
    p.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv).",
    )


def _parse_instructions(sets: List[str], unsets: List[str], renames: List[str]) -> List[PatchInstruction]:
    instructions: List[PatchInstruction] = []
    for item in sets:
        if "=" not in item:
            print(f"[patch] invalid --set value (expected KEY=VALUE): {item}", file=sys.stderr)
            sys.exit(2)
        key, _, value = item.partition("=")
        instructions.append(PatchInstruction(op="set", key=key.strip(), value=value))
    for key in unsets:
        instructions.append(PatchInstruction(op="unset", key=key.strip()))
    for item in renames:
        if "=" not in item:
            print(f"[patch] invalid --rename value (expected OLD=NEW): {item}", file=sys.stderr)
            sys.exit(2)
        old, _, new = item.partition("=")
        instructions.append(PatchInstruction(op="rename", key=old.strip(), new_key=new.strip()))
    return instructions


def run_patch(args: argparse.Namespace) -> int:
    env = load_env_file(args.env_file)
    instructions = _parse_instructions(args.sets, args.unsets, args.renames)
    result = apply_patch(env, instructions, allow_overwrite=not args.no_overwrite)

    if args.format == "json":
        print(json.dumps(result.env, indent=2, sort_keys=True))
    else:
        for key, value in sorted(result.env.items()):
            print(f"{key}={value}")

    print(f"# {result.summary()}", file=sys.stderr)
    return 0
