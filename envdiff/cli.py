"""Command-line interface for envdiff."""

import sys
import argparse
from typing import List, Optional

from envdiff.loader import load_env_file, load_from_os_environ
from envdiff.comparator import compare_envs
from envdiff.reporter import render, OutputFormat


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare environment variable configurations across deployment targets.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Paths to .env files to compare (exactly 2 required unless --os-env is used).",
    )
    parser.add_argument(
        "--os-env",
        action="store_true",
        help="Use the current OS environment as the second source.",
    )
    parser.add_argument(
        "--label-a",
        default=None,
        metavar="LABEL",
        help="Label for the first environment (defaults to file path).",
    )
    parser.add_argument(
        "--label-b",
        default=None,
        metavar="LABEL",
        help="Label for the second environment (defaults to file path or 'os.environ').",
    )
    parser.add_argument(
        "--format",
        choices=[f.value for f in OutputFormat],
        default=OutputFormat.TEXT.value,
        dest="output_format",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if differences are found.",
    )
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.os_env:
        if len(args.files) != 1:
            parser.error("Exactly one FILE is required when --os-env is used.")
        env_a = load_env_file(args.files[0])
        env_b = load_from_os_environ()
        label_a = args.label_a or args.files[0]
        label_b = args.label_b or "os.environ"
    else:
        if len(args.files) != 2:
            parser.error("Exactly two FILE arguments are required.")
        env_a = load_env_file(args.files[0])
        env_b = load_env_file(args.files[1])
        label_a = args.label_a or args.files[0]
        label_b = args.label_b or args.files[1]

    result = compare_envs(env_a, env_b)
    fmt = OutputFormat(args.output_format)
    print(render(result, fmt, label_a=label_a, label_b=label_b))

    if args.exit_code and result.has_differences():
        return 1
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
