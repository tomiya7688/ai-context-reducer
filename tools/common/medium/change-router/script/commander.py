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
    if explicit_changed:
        changed_ok = True
        changed = explicit_changed
        changed_source = 'explicit'
    else:
        changed_ok, changed = changed_files(root, base)
        changed_source = 'git_diff'

    if not changed_ok:
        return {
            'tool': 'change-router',
            'status': 'git_diff_unavailable',
            'changed_source': changed_source,
            'changed_files': [],
            'changed_files_truncated': False,
            'index_candidates': 0,
            'index_truncated': False,
            'routes': [],
        }

    changed_truncated = max_changed > 0 and len(changed) > max_changed
    if max_changed > 0:
        changed = changed[:max_changed]

    index, index_truncated = candidate_index(root, max_index_files)
    routes = [route_candidates(rel, index, candidate_limit) for rel in changed]

    return {
        'tool': 'change-router',
        'status': 'ok',
        'changed_source': changed_source,
        'changed_files': changed,
        'changed_files_truncated': changed_truncated,
        'index_candidates': len(index),
        'index_truncated': index_truncated,
        'routes': routes,
    }
