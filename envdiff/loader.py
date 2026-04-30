"""Loaders for reading environment variable configurations from various sources."""

import os
from pathlib import Path
from typing import Dict, Optional


def load_env_file(filepath: str | Path) -> Dict[str, str]:
    """Load environment variables from a .env file.

    Supports KEY=VALUE format, ignores blank lines and comments (#).

    Args:
        filepath: Path to the .env file.

    Returns:
        Dictionary of environment variable key-value pairs.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If a line has an invalid format.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Environment file not found: {filepath}")

    env_vars: Dict[str, str] = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Invalid format at line {lineno} in {filepath}: '{line}'"
                )
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if not key:
                raise ValueError(
                    f"Empty key at line {lineno} in {filepath}: '{line}'"
                )
            env_vars[key] = value

    return env_vars


def load_from_os_environ(prefix: Optional[str] = None) -> Dict[str, str]:
    """Load environment variables from the current OS environment.

    Args:
        prefix: Optional prefix to filter variables (e.g., 'APP_').

    Returns:
        Dictionary of environment variable key-value pairs.
    """
    if prefix:
        return {
            k: v for k, v in os.environ.items() if k.startswith(prefix)
        }
    return dict(os.environ)
