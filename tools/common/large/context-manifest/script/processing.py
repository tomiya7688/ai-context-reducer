from __future__ import annotations

from pathlib import Path

HIGH = {'README.md', 'AI_CONTEXT.md', 'AGENTS.md', 'CLAUDE.md', 'pyproject.toml', 'package.json', 'Cargo.toml', 'go.mod'}
ORDER = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4}
SOURCE_EXTS = {'.py', '.cs', '.go', '.rs', '.ts', '.js', '.cpp', '.c', '.h', '.java'}


def priority(path: Path) -> str:
    name = path.name
    text = path.as_posix().lower()
    if name in HIGH:
        return 'P0'
    if '/tests/' in '/' + text or text.startswith('tests/'):
        return 'P2'
    if '/docs/' in '/' + text or text.startswith('docs/'):
        return 'P3'
    if path.suffix.lower() in SOURCE_EXTS:
        return 'P1'
    return 'P4'


def build_manifest(
    entries: list[dict[str, object]],
    limit: int,
    stat_error_count: int = 0,
    walk_error_count: int = 0,
) -> dict[str, object]:
    limit = max(0, limit)
    rows = [
        {
            'context_priority': priority(entry['path']),
            'path': entry['path'].as_posix(),
            'bytes': entry['bytes'],
        }
        for entry in entries
    ]
    rows.sort(key=lambda row: (ORDER[row['context_priority']], row['path']))
    errors = stat_error_count + walk_error_count
    returned = rows[:limit] if limit > 0 else []
    return {
        'tool': 'context-manifest',
        'status': 'ok_with_warnings' if errors else 'ok',
        'total_files': len(rows),
        'returned_files': len(returned),
        'stat_error_count': stat_error_count,
        'walk_error_count': walk_error_count,
        'files_truncated': len(rows) > len(returned),
        'files': returned,
    }
