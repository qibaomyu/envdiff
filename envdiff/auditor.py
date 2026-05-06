"""Audit trail: record and replay comparison sessions for reproducibility."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

AUDIT_VERSION = "1.0"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_audit(
    sources: List[str],
    env_data: Dict[str, Dict[str, str]],
    result_summary: Dict[str, Any],
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """Build an audit record dict from a comparison session."""
    return {
        "audit_version": AUDIT_VERSION,
        "timestamp": _now_iso(),
        "label": label or "",
        "sources": sources,
        "env_data": env_data,
        "result_summary": result_summary,
    }


def save_audit(audit: Dict[str, Any], path: str) -> None:
    """Persist an audit record to a JSON file."""
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(audit, fh, indent=2)


def load_audit(path: str) -> Dict[str, Any]:
    """Load an audit record from a JSON file."""
    dest = Path(path)
    if not dest.exists():
        raise FileNotFoundError(f"Audit file not found: {path}")
    with dest.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("audit_version") != AUDIT_VERSION:
        raise ValueError(
            f"Unsupported audit version: {data.get('audit_version')!r}"
        )
    return data


def audit_summary(audit: Dict[str, Any]) -> str:
    """Return a human-readable one-line summary of an audit record."""
    label = audit.get("label") or "(no label)"
    ts = audit.get("timestamp", "unknown time")
    sources = ", ".join(audit.get("sources", []))
    rs = audit.get("result_summary", {})
    has_diff = rs.get("has_differences", False)
    status = "DIFFERENCES FOUND" if has_diff else "no differences"
    return f"[{ts}] {label} | sources: {sources} | {status}"
