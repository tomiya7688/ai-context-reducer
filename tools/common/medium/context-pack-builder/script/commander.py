from __future__ import annotations

from pathlib import Path

from messenger import git_lines
from processing import render_context_pack


def build_context_pack(root: Path, task: dict[str, str], limit: int = 60) -> str:
    changed_all = git_lines(root, ['diff', '--name-only', 'HEAD'])
    status_all = git_lines(root, ['status', '--short'])
    state = {
        'changed': changed_all[:limit],
        'status': status_all[:limit],
        'changed_truncated': len(changed_all) > limit,
        'status_truncated': len(status_all) > limit,
    }
    return render_context_pack(task, state)
