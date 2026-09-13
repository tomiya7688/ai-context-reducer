from __future__ import annotations

from pathlib import Path

from messenger import git_text
from processing import render_remote_delta


def build_remote_delta(root: Path, base: str, remote: str, max_files: int) -> str:
    status = git_text(root, 'status', '--short')
    if not git_text(root, 'rev-parse', '--verify', remote):
        return render_remote_delta({'remote_available': False, 'dirty': bool(status)}, max_files)

    data = {
        'remote_available': True,
        'dirty': bool(status),
        'ahead': git_text(root, 'rev-list', '--count', f'{remote}..{base}') or '0',
        'behind': git_text(root, 'rev-list', '--count', f'{base}..{remote}') or '0',
        'changed_files': git_text(root, 'diff', '--name-only', base, remote).splitlines(),
        'stat': git_text(root, 'diff', '--shortstat', base, remote),
        'remote_commits': git_text(root, 'log', '--oneline', '--max-count=8', f'{base}..{remote}').splitlines(),
    }
    return render_remote_delta(data, max_files)
