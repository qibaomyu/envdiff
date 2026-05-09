"""Archive multiple env snapshots into a single bundle for portability."""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

ARCHIVE_VERSION = "1.0"


@dataclass
class ArchiveEntry:
    label: str
    env: Dict[str, str]
    captured_at: str
    checksum: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ArchiveEntry label={self.label!r} keys={len(self.env)}>"


@dataclass
class EnvArchive:
    entries: List[ArchiveEntry] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = ARCHIVE_VERSION

    def add(self, label: str, env: Dict[str, str], captured_at: Optional[str] = None) -> ArchiveEntry:
        ts = captured_at or datetime.now(timezone.utc).isoformat()
        checksum = _checksum(env)
        entry = ArchiveEntry(label=label, env=env, captured_at=ts, checksum=checksum)
        self.entries.append(entry)
        return entry

    def labels(self) -> List[str]:
        return [e.label for e in self.entries]

    def get(self, label: str) -> Optional[ArchiveEntry]:
        for entry in self.entries:
            if entry.label == label:
                return entry
        return None


def _checksum(env: Dict[str, str]) -> str:
    payload = json.dumps(env, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def save_archive(archive: EnvArchive, path: Path) -> None:
    data = {
        "version": archive.version,
        "created_at": archive.created_at,
        "entries": [
            {
                "label": e.label,
                "env": e.env,
                "captured_at": e.captured_at,
                "checksum": e.checksum,
            }
            for e in archive.entries
        ],
    }
    path.write_text(json.dumps(data, indent=2))


def load_archive(path: Path) -> EnvArchive:
    data = json.loads(path.read_text())
    archive = EnvArchive(created_at=data["created_at"], version=data["version"])
    for raw in data.get("entries", []):
        entry = ArchiveEntry(
            label=raw["label"],
            env={str(k): str(v) for k, v in raw["env"].items()},
            captured_at=raw["captured_at"],
            checksum=raw["checksum"],
        )
        archive.entries.append(entry)
    return archive
