"""CLI subcommand: archive — bundle and inspect env snapshot archives."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.archiver import EnvArchive, load_archive, save_archive
from envdiff.loader import load_env_file


def add_archive_args(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("archive", help="Bundle env files into an archive")
    sub = p.add_subparsers(dest="archive_cmd", required=True)

    # archive add
    add_p = sub.add_parser("add", help="Add an env file to an archive")
    add_p.add_argument("archive_file", help="Path to archive JSON")
    add_p.add_argument("env_file", help="Env file to add")
    add_p.add_argument("--label", required=True, help="Label for this entry")

    # archive list
    list_p = sub.add_parser("list", help="List entries in an archive")
    list_p.add_argument("archive_file", help="Path to archive JSON")
    list_p.add_argument("--format", choices=["text", "json"], default="text")

    # archive show
    show_p = sub.add_parser("show", help="Show a single archive entry")
    show_p.add_argument("archive_file", help="Path to archive JSON")
    show_p.add_argument("label", help="Label of the entry to show")
    show_p.add_argument("--format", choices=["text", "json"], default="text")


def run_archive(args: argparse.Namespace) -> int:
    cmd = args.archive_cmd
    if cmd == "add":
        return _run_add(args)
    if cmd == "list":
        return _run_list(args)
    if cmd == "show":
        return _run_show(args)
    return 1  # pragma: no cover


def _run_add(args: argparse.Namespace) -> int:
    archive_path = Path(args.archive_file)
    if archive_path.exists():
        archive = load_archive(archive_path)
    else:
        archive = EnvArchive()

    env = load_env_file(Path(args.env_file))
    archive.add(args.label, env)
    save_archive(archive, archive_path)
    print(f"Added '{args.label}' to {archive_path} ({len(env)} keys)")
    return 0


def _run_list(args: argparse.Namespace) -> int:
    archive = load_archive(Path(args.archive_file))
    if args.format == "json":
        out = [
            {"label": e.label, "keys": len(e.env), "captured_at": e.captured_at, "checksum": e.checksum}
            for e in archive.entries
        ]
        print(json.dumps(out, indent=2))
    else:
        if not archive.entries:
            print("(no entries)")
        for entry in archive.entries:
            print(f"{entry.label:30s}  keys={len(entry.env):4d}  checksum={entry.checksum}  at={entry.captured_at}")
    return 0


def _run_show(args: argparse.Namespace) -> int:
    archive = load_archive(Path(args.archive_file))
    entry = archive.get(args.label)
    if entry is None:
        print(f"Error: label '{args.label}' not found in archive", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps({"label": entry.label, "env": entry.env, "captured_at": entry.captured_at}, indent=2))
    else:
        print(f"Label     : {entry.label}")
        print(f"Captured  : {entry.captured_at}")
        print(f"Checksum  : {entry.checksum}")
        print(f"Keys ({len(entry.env)}):")
        for k, v in sorted(entry.env.items()):
            print(f"  {k}={v}")
    return 0
