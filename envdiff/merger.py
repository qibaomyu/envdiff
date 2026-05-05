"""Merge multiple env configurations into a unified baseline or diff-aware output."""

from typing import Dict, List, Optional, Set

EnvMap = Dict[str, str]


class MergeStrategy:
    UNION = "union"
    INTERSECTION = "intersection"
    FIRST_WINS = "first_wins"
    LAST_WINS = "last_wins"


def merge_envs(
    envs: List[EnvMap],
    strategy: str = MergeStrategy.UNION,
    labels: Optional[List[str]] = None,
) -> EnvMap:
    """Merge a list of env dicts into a single dict using the given strategy.

    Args:
        envs: List of environment variable dicts to merge.
        strategy: One of 'union', 'intersection', 'first_wins', 'last_wins'.
        labels: Optional labels for each env (used in conflict metadata, ignored here).

    Returns:
        A merged EnvMap.
    """
    if not envs:
        return {}

    if strategy == MergeStrategy.UNION:
        merged: EnvMap = {}
        for env in envs:
            for key, value in env.items():
                if key not in merged:
                    merged[key] = value
        return merged

    elif strategy == MergeStrategy.INTERSECTION:
        common_keys: Set[str] = set(envs[0].keys())
        for env in envs[1:]:
            common_keys &= set(env.keys())
        # Use values from first env for common keys
        return {key: envs[0][key] for key in common_keys}

    elif strategy == MergeStrategy.FIRST_WINS:
        merged = {}
        for env in envs:
            for key, value in env.items():
                if key not in merged:
                    merged[key] = value
        return merged

    elif strategy == MergeStrategy.LAST_WINS:
        merged = {}
        for env in envs:
            merged.update(env)
        return merged

    else:
        raise ValueError(f"Unknown merge strategy: {strategy!r}")


def find_conflicts(envs: List[EnvMap], labels: Optional[List[str]] = None) -> Dict[str, Dict[str, str]]:
    """Identify keys that have differing values across env maps.

    Returns:
        A dict mapping conflicting key -> {label: value} for each env.
    """
    if not envs:
        return {}

    resolved_labels = labels if labels else [str(i) for i in range(len(envs))]
    all_keys: Set[str] = set()
    for env in envs:
        all_keys |= set(env.keys())

    conflicts: Dict[str, Dict[str, str]] = {}
    for key in all_keys:
        values = {label: env[key] for label, env in zip(resolved_labels, envs) if key in env}
        unique_values = set(values.values())
        if len(unique_values) > 1:
            conflicts[key] = values

    return conflicts
