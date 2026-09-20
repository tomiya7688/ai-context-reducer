from __future__ import annotations

import os
from pathlib import Path

DOC_EXTS = {'.md', '.txt', '.rst'}
IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor', 'generated',
}


# iter_documents はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def iter_documents(root: Path, scan_stats: dict[str, int] | None = None):
    stats = scan_stats if scan_stats is not None else {'walk_error_count': 0}
    stats.setdefault('walk_error_count', 0)

    # on_walk_error はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
    def on_walk_error(_error: OSError) -> None:
        stats['walk_error_count'] += 1

    for current, dirs, files in os.walk(root, onerror=on_walk_error):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE_DIRS)
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            if path.suffix.lower() in DOC_EXTS:
                yield path


# read_lines は必要な入力だけを読み込み、後段が扱いやすい形へ整える。
def read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError:
        return None
