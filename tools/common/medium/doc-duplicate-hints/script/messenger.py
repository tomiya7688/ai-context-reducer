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

# on_walk_error は文書scan中に列挙できないdirectoryとfailure countを残します。
    def on_walk_error(_error: OSError) -> None:
        stats['walk_error_count'] += 1

    for current, dirs, files in os.walk(root, onerror=on_walk_error):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE_DIRS)
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            if path.suffix.lower() in DOC_EXTS:
                yield path


# read_lines は類似比較に使うheadingと本文行を読み、文字code位置を保持します。
def read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError:
        return None
