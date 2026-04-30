"""Core comparison logic for environment variable configurations."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class EnvDiffResult:
    """Holds the result of comparing two environment configurations."""

    target_a: str
    target_b: str
    only_in_a: Dict[str, str] = field(default_factory=dict)
    only_in_b: Dict[str, str] = field(default_factory=dict)
    value_differs: Dict[str, tuple] = field(default_factory=dict)  # key -> (val_a, val_b)
    common_keys: Set[str] = field(default_factory=set)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_a or self.only_in_b or self.value_differs)

    @property
    def summary(self) -> str:
        lines = [f"Diff: {self.target_a} vs {self.target_b}"]
        lines.append(f"  Only in {self.target_a}: {len(self.only_in_a)} key(s)")
        lines.append(f"  Only in {self.target_b}: {len(self.only_in_b)} key(s)")
        lines.append(f"  Value differences: {len(self.value_differs)} key(s)")
        lines.append(f"  Common identical keys: {len(self.common_keys)}")
        return "\n".join(lines)


def compare_envs(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
    target_a: str = "target_a",
    target_b: str = "target_b",
    ignore_keys: Optional[List[str]] = None,
) -> EnvDiffResult:
    """Compare two environment variable dictionaries.

    Args:
        env_a: First environment config.
        env_b: Second environment config.
        target_a: Label for the first target.
        target_b: Label for the second target.
        ignore_keys: List of keys to exclude from comparison.

    Returns:
        EnvDiffResult with detailed comparison data.
    """
    ignored = set(ignore_keys or [])
    keys_a = set(env_a.keys()) - ignored
    keys_b = set(env_b.keys()) - ignored

    result = EnvDiffResult(target_a=target_a, target_b=target_b)
    result.only_in_a = {k: env_a[k] for k in keys_a - keys_b}
    result.only_in_b = {k: env_b[k] for k in keys_b - keys_a}

    for key in keys_a & keys_b:
        if env_a[key] == env_b[key]:
            result.common_keys.add(key)
        else:
            result.value_differs[key] = (env_a[key], env_b[key])

    return result
