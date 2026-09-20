from __future__ import annotations

from pathlib import Path

from messenger import candidate_index, changed_files
from processing import route_candidates


# _dedupe はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


# route_changes はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def route_changes(
    root: Path,
    base: str | None,
    explicit_changed: list[str],
    max_changed: int,
    max_index_files: int,
    candidate_limit: int,
) -> dict[str, object]:
    if explicit_changed:
        changed_result = {'ok': True, 'lines': _dedupe(explicit_changed), 'error_kind': None}
        changed_source = 'explicit'
    else:
        changed_result = changed_files(root, base)
        changed_source = 'git_diff'

    if not changed_result['ok']:
        return {
            'tool': 'change-router',
            'status': 'git_diff_unavailable',
            'git_error_kind': changed_result.get('error_kind'),
            'changed_source': changed_source,
            'changed_files': [],
            'changed_files_truncated': False,
            'index_candidates': 0,
            'index_truncated': False,
            'index_walk_error_count': 0,
            'routes': [],
        }

    changed = _dedupe(list(changed_result['lines']))
    max_changed = max(0, max_changed)
    max_index_files = max(0, max_index_files)
    candidate_limit = max(0, candidate_limit)
    changed_truncated = max_changed > 0 and len(changed) > max_changed
    if max_changed > 0:
        changed = changed[:max_changed]

    index, index_truncated, walk_error_count = candidate_index(root, max_index_files)
    routes = [route_candidates(rel, index, candidate_limit) for rel in changed]

    return {
        'tool': 'change-router',
        'status': 'ok_with_warnings' if walk_error_count else 'ok',
        'changed_source': changed_source,
        'changed_files': changed,
        'changed_files_truncated': changed_truncated,
        'index_candidates': len(index),
        'index_truncated': index_truncated,
        'index_walk_error_count': walk_error_count,
        'routes': routes,
    }
