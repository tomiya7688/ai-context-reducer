from __future__ import annotations

import os
from pathlib import Path

IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', 'bin', 'obj',
    'build', 'dist', '__pycache__', '.godot', '.idea', '.vs', 'vendor',
}


def collect_files(root: Path) -> tuple[list[dict[str, object]], dict[str, int]]:
    rows: list[dict[str, object]] = []
    stats = {'stat_error_count': 0, 'walk_error_count': 0}

    def on_walk_error(_error: OSError) -> None:
        stats['walk_error_count'] += 1

    for current, dirs, files in os.walk(root, onerror=on_walk_error):
        dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            try:
                size = path.stat().st_size
            except OSError:
                stats['stat_error_count'] += 1
                continue
            rows.append({'path': path.relative_to(root), 'bytes': size})
    return rows, stats
