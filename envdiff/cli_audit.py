"""CLI sub-commands for audit: save and inspect audit records."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.auditor import audit_summary, load_audit, record_audit, save_audit
from envdiff.comparator import compare_envs
from envdiff.loader import load_env_file


def add_audit_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'audit' sub-commands."""
    audit_parser = subparsers.add_parser("audit", help="Audit comparison sessions")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd", required=True)

    # save
    save_p = audit_sub.add_parser("save", help="Run a comparison and save audit record")
    save_p.add_argument("files", nargs="+", metavar="FILE", help="Env files to compare")
    save_p.add_argument("-o", "--output", required=True, help="Destination audit JSON file")
    save_p.add_argument("--label", default="", help="Optional label for this audit")

    # show
    show_p = audit_sub.add_parser("show", help="Display summary of a saved audit record")
    show_p.add_argument("audit_file", help="Path to audit JSON file")


def run_audit(args: argparse.Namespace) -> int:
    """Dispatch audit sub-commands; return exit code."""
    if args.audit_cmd == "save":
        return _run_save(args)
    if args.audit_cmd == "show":
        return _run_show(args)
    return 1


def _run_save(args: argparse.Namespace) -> int:
    if len(args.files) < 2:
        print("error: at least two files are required for comparison", file=sys.stderr)
        return 2

    envs = {}
    for path in args.files:
        try:
            envs[path] = load_env_file(path)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    file_list: List[str] = list(envs.keys())
    result = compare_envs(envs[file_list[0]], envs[file_list[1]])
    summary = {
        "has_differences": result.has_differences(),
        "only_in_a": sorted(result.only_in_a),
        "only_in_b": sorted(result.only_in_b),
        "value_differs": sorted(result.value_differs),
    }
    audit = record_audit(
        sources=file_list,
        env_data={k: dict(v) for k, v in envs.items()},
        result_summary=summary,
        label=args.label,
    )
    save_audit(audit, args.output)
    print(f"Audit saved to {args.output}")
    return 0


def _run_show(args: argparse.Namespace) -> int:
    try:
        audit = load_audit(args.audit_file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(audit_summary(audit))
    return 0
