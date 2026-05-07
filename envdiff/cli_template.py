"""CLI sub-command: render an env template using key=value sources."""

from __future__ import annotations

import argparse
import sys

from envdiff.loader import load_env_file, load_from_os_environ
from envdiff.templater import TemplateRenderError, render_template_file


def add_template_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "template",
        help="Render a template file using env variables as substitution values.",
    )
    parser.add_argument(
        "template",
        metavar="TEMPLATE",
        help="Path to the template file containing {{ KEY }} placeholders.",
    )
    parser.add_argument(
        "--env",
        metavar="FILE",
        action="append",
        dest="env_files",
        default=[],
        help="Env file(s) to load values from (can be repeated).",
    )
    parser.add_argument(
        "--from-os",
        action="store_true",
        default=False,
        help="Also include variables from the current OS environment.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with error if any placeholder cannot be resolved.",
    )
    parser.add_argument(
        "--default",
        metavar="VALUE",
        default=None,
        help="Fallback value for unresolved placeholders (only in non-strict mode).",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write rendered output to FILE instead of stdout.",
    )


def run_template(args: argparse.Namespace) -> int:
    """Execute the *template* sub-command; return an exit code."""
    env: dict[str, str] = {}

    if args.from_os:
        env.update(load_from_os_environ())

    for path in args.env_files:
        try:
            env.update(load_env_file(path))
        except FileNotFoundError:
            print(f"error: env file not found: {path}", file=sys.stderr)
            return 2

    try:
        rendered = render_template_file(
            args.template,
            env,
            strict=args.strict,
            default=args.default,
        )
    except FileNotFoundError:
        print(f"error: template file not found: {args.template}", file=sys.stderr)
        return 2
    except TemplateRenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(rendered)
    else:
        print(rendered, end="")

    return 0
