"""CLI sub-command: encrypt / decrypt env values."""

from __future__ import annotations

import argparse
import getpass
import sys
from typing import List

from envdiff.encryptor import decrypt_env, encrypt_env
from envdiff.loader import load_env_file


def add_encrypt_args(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "encrypt",
        help="Encrypt or decrypt values in an env file.",
    )
    p.add_argument("env_file", help="Path to the .env file.")
    p.add_argument(
        "--mode",
        choices=["encrypt", "decrypt"],
        default="encrypt",
        help="Operation mode (default: encrypt).",
    )
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Keys to encrypt (required in encrypt mode).",
    )
    p.add_argument(
        "--passphrase",
        metavar="PASSPHRASE",
        help="Passphrase for key derivation (prompted if omitted).",
    )
    p.set_defaults(func=run_encrypt)


def _get_passphrase(args: argparse.Namespace) -> str:
    if args.passphrase:
        return args.passphrase
    return getpass.getpass("Passphrase: ")


def run_encrypt(args: argparse.Namespace) -> int:
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    passphrase = _get_passphrase(args)

    if args.mode == "encrypt":
        if not args.keys:
            print(
                "Error: --keys is required in encrypt mode.",
                file=sys.stderr,
            )
            return 1
        result = encrypt_env(env, args.keys, passphrase)
        print(result.summary())
        for k, v in result.encrypted.items():
            print(f"  {k}={v}")
        return 0

    # decrypt mode
    result = decrypt_env(env, passphrase)
    print(result.summary())
    if result.failed:
        print("Failed keys:", ", ".join(result.failed), file=sys.stderr)
    for k, v in result.decrypted.items():
        print(f"  {k}={v}")
    return 0 if not result.failed else 1
