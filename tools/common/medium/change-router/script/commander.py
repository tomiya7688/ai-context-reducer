from __future__ import annotations

from pathlib import Path

from messenger import candidate_index, changed_files
from processing import route_candidates


def route_changes(
    root: Path,
    base: str | None,
    explicit_changed: list[str],
    max_changed: int,
    max_index_files: int,
    candidate_limit: int,
) -> dict[str, object]:
    changed = explicit_changed or changed_files(root, base)
    changed_truncated = len(changed) > max_changed
    changed = changed[:max_changed]

    index, index_truncated = candidate_index(root, max_index_files)
    routes = [route_candidates(rel, index, candidate_limit) for rel in changed]

    return {
        'routes': routes,
        'changed_count': len(changed),
        'index_candidates': len(index),
        'truncated': {
            'changed': changed_truncated,
            'index': index_truncated,
        },
    }
