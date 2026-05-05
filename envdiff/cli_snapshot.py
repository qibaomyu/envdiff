"""CLI sub-commands for snapshot management (save / inspect)."""

import argparse
import json
import sys
from typing import List, Optional

from envdiff.loader import load_env_file, load_from_os_environ
from envdiff.snapshot import save_snapshot, load_snapshot, snapshot_metadata


def add_snapshot_args(subparsers) -> None:
    """Register 'snapshot' sub-commands onto an existing subparsers object."""
    snap_parser = subparsers.add_parser(
        "snapshot", help="Save or inspect environment snapshots"
    )
    snap_sub = snap_parser.add_subparsers(dest="snap_cmd", required=True)

    # --- save ---
    save_p = snap_sub.add_parser("save", help="Save an env file as a snapshot")
    save_p.add_argument("env_file", nargs="?", help="Path to .env file (omit to capture os.environ)")
    save_p.add_argument("output", help="Destination snapshot JSON file")
    save_p.add_argument("--label", default=None, help="Human-readable label for this snapshot")
    save_p.add_argument("--meta", nargs="*", metavar="KEY=VALUE", help="Extra metadata pairs")

    # --- inspect ---
    inspect_p = snap_sub.add_parser("inspect", help="Print metadata of a snapshot")
    inspect_p.add_argument("snapshot", help="Path to snapshot JSON file")


def _parse_meta(pairs: Optional[List[str]]) -> dict:
    result = {}
    for pair in (pairs or []):
        if "=" not in pair:
            raise argparse.ArgumentTypeError(f"Invalid metadata pair: {pair!r}")
        k, v = pair.split("=", 1)
        result[k.strip()] = v.strip()
    return result


def run_snapshot(args: argparse.Namespace) -> int:
    """Dispatch snapshot sub-commands; returns exit code."""
    if args.snap_cmd == "save":
        if args.env_file:
            env = load_env_file(args.env_file)
        else:
            env = load_from_os_environ()
        meta = _parse_meta(getattr(args, "meta", None))
        save_snapshot(env, args.output, label=args.label, metadata=meta)
        print(f"Snapshot saved to {args.output!r} ({len(env)} keys).")
        return 0

    if args.snap_cmd == "inspect":
        meta = snapshot_metadata(args.snapshot)
        env = load_snapshot(args.snapshot)
        print(json.dumps({**meta, "key_count": len(env)}, indent=2))
        return 0

    print(f"Unknown snapshot command: {args.snap_cmd}", file=sys.stderr)
    return 1
