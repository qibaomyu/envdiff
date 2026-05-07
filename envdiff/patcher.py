"""Apply a set of patch operations (set, unset, rename) to an env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

PatchOp = Literal["set", "unset", "rename"]


@dataclass
class PatchInstruction:
    op: PatchOp
    key: str
    value: Optional[str] = None   # used by "set"
    new_key: Optional[str] = None  # used by "rename"

    def __repr__(self) -> str:  # pragma: no cover
        if self.op == "set":
            return f"PatchInstruction(set {self.key}={self.value!r})"
        if self.op == "unset":
            return f"PatchInstruction(unset {self.key})"
        return f"PatchInstruction(rename {self.key} -> {self.new_key})"


@dataclass
class PatchResult:
    env: Dict[str, str]
    applied: List[PatchInstruction] = field(default_factory=list)
    skipped: List[PatchInstruction] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"{len(self.applied)} applied, {len(self.skipped)} skipped"
        )


def apply_patch(
    env: Dict[str, str],
    instructions: List[PatchInstruction],
    *,
    allow_overwrite: bool = True,
) -> PatchResult:
    """Return a new env dict with *instructions* applied.

    Args:
        env: The source environment mapping.
        instructions: Ordered list of patch operations to apply.
        allow_overwrite: When False, a ``set`` targeting an existing key is
            skipped instead of overwriting it.
    """
    result = dict(env)
    applied: List[PatchInstruction] = []
    skipped: List[PatchInstruction] = []

    for instr in instructions:
        if instr.op == "set":
            if not allow_overwrite and instr.key in result:
                skipped.append(instr)
            else:
                result[instr.key] = instr.value or ""
                applied.append(instr)

        elif instr.op == "unset":
            if instr.key in result:
                del result[instr.key]
                applied.append(instr)
            else:
                skipped.append(instr)

        elif instr.op == "rename":
            if instr.key not in result or not instr.new_key:
                skipped.append(instr)
            else:
                result[instr.new_key] = result.pop(instr.key)
                applied.append(instr)

        else:  # pragma: no cover
            skipped.append(instr)

    return PatchResult(env=result, applied=applied, skipped=skipped)
