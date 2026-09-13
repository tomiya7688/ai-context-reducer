from __future__ import annotations

from pathlib import Path

from messenger import git_lines
from processing import render_context_pack


def build_context_pack(root: Path, task: dict[str, str], limit: int = 60) -> str:
    changed_result = git_lines(root, ['diff', '--name-only', 'HEAD'])
    status_result = git_lines(root, ['status', '--short'])
    changed_all = list(changed_result['lines'])
    status_all = list(status_result['lines'])
    state = {
        'changed': changed_all[:limit],
        'status': status_all[:limit],
        'changed_query_ok': changed_result['ok'],
        'status_query_ok': status_result['ok'],
        'changed_truncated': len(changed_all) > limit,
        'status_truncated': len(status_all) > limit,
    }
    return render_context_pack(task, state)
