from __future__ import annotations

from pathlib import Path

from messenger import git_result
from processing import compact_remote_delta


# _int_or_none は整数文字列を変換し、parse不能な値をNoneで示します。
def _int_or_none(text: str) -> int | None:
    try:
        return int(text)
    except ValueError:
        return None


# build_remote_delta は解析結果を後段で再利用できる構造へ組み立てる。
def build_remote_delta(root: Path, base: str, remote: str, max_files: int) -> dict[str, object]:
    repository_ok, _, repository_error = git_result(root, 'rev-parse', '--is-inside-work-tree')
    if not repository_ok:
        status = 'git_unavailable' if repository_error == 'git_unavailable' else 'git_unavailable_or_not_repository'
        return compact_remote_delta({
            'status': status,
            'base': base,
            'remote': remote,
            'dirty': None,
        }, max_files)

    status_ok, status_text, _ = git_result(root, 'status', '--short')
    if not status_ok:
        return compact_remote_delta({
            'status': 'git_query_failed', 'base': base, 'remote': remote, 'dirty': None,
        }, max_files)

    remote_ok, _, _ = git_result(root, 'rev-parse', '--verify', remote)
    if not remote_ok:
        reference = remote if remote.startswith('refs/') else f'refs/remotes/{remote}'
        reference_ok, _, reference_error = git_result(root, 'show-ref', '--verify', '--quiet', reference)
        if not reference_ok:
            error_status = 'remote_unavailable' if reference_error == 'remote_unavailable' else 'git_query_failed'
            return compact_remote_delta({
                'status': error_status, 'base': base, 'remote': remote, 'dirty': bool(status_text),
            }, max_files)
        return compact_remote_delta({
            'status': 'git_query_failed', 'base': base, 'remote': remote, 'dirty': bool(status_text),
        }, max_files)

    ahead_ok, ahead_text, _ = git_result(root, 'rev-list', '--count', f'{remote}..{base}')
    behind_ok, behind_text, _ = git_result(root, 'rev-list', '--count', f'{base}..{remote}')
    names_ok, names_text, _ = git_result(root, 'diff', '--name-only', base, remote)
    stat_ok, stat_text, _ = git_result(root, 'diff', '--shortstat', base, remote)
    commits_ok, commits_text, _ = git_result(root, 'log', '--oneline', '--max-count=8', f'{base}..{remote}')

    if not all((ahead_ok, behind_ok, names_ok, stat_ok, commits_ok)):
        return compact_remote_delta({
            'status': 'git_query_failed',
            'base': base,
            'remote': remote,
            'dirty': bool(status_text),
        }, max_files)

    return compact_remote_delta({
        'status': 'ok',
        'base': base,
        'remote': remote,
        'dirty': bool(status_text),
        'ahead': _int_or_none(ahead_text),
        'behind': _int_or_none(behind_text),
        'diff_stat': stat_text or None,
        'changed_files': [line for line in names_text.splitlines() if line],
        'remote_commits': [line for line in commits_text.splitlines() if line],
    }, max_files)
