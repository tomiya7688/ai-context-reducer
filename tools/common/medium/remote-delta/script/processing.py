from __future__ import annotations


def compact_remote_delta(data: dict[str, object], max_files: int) -> dict[str, object]:
    names = list(data.get('changed_files', []))
    commits = list(data.get('remote_commits', []))
    return {
        'tool': 'remote-delta',
        'status': data.get('status', 'error'),
        'base': data.get('base'),
        'remote': data.get('remote'),
        'dirty': data.get('dirty'),
        'ahead': data.get('ahead'),
        'behind': data.get('behind'),
        'diff_stat': data.get('diff_stat'),
        'changed_files': names[:max_files],
        'changed_files_truncated': len(names) > max_files,
        'remote_commits': commits,
    }
