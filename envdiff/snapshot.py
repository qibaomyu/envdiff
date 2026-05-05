"""Snapshot management: save and load environment snapshots for later comparison."""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional

SNAPSHOT_VERSION = 1


def save_snapshot(
    env: Dict[str, str],
    path: str,
    label: Optional[str] = None,
    metadata: Optional[Dict] = None,
) -> None:
    """Persist an environment dict to a JSON snapshot file."""
    payload = {
        "version": SNAPSHOT_VERSION,
        "label": label or os.path.splitext(os.path.basename(path))[0],
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
        "env": env,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)


def load_snapshot(path: str) -> Dict[str, str]:
    """Load an environment dict from a JSON snapshot file.

    Returns only the ``env`` mapping; raises ValueError for unsupported versions.
    """
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)

    version = payload.get("version")
    if version != SNAPSHOT_VERSION:
        raise ValueError(
            f"Unsupported snapshot version {version!r} in {path!r}. "
            f"Expected {SNAPSHOT_VERSION}."
        )

    env = payload.get("env")
    if not isinstance(env, dict):
        raise ValueError(f"Snapshot {path!r} is missing a valid 'env' mapping.")

    return {str(k): str(v) for k, v in env.items()}


def snapshot_metadata(path: str) -> Dict:
    """Return the metadata block (label, captured_at, metadata) without the env."""
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return {
        "label": payload.get("label"),
        "captured_at": payload.get("captured_at"),
        "metadata": payload.get("metadata", {}),
        "version": payload.get("version"),
    }
