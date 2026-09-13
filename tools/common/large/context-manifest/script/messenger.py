from __future__ import annotations

import os
from pathlib import Path

IGNORE_DIRS = {'.git', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist', '__pycache__'}


def collect_files(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            try:
                size = path.stat().st_size
            except OSError:
                continue
            rows.append({'path': path.relative_to(root), 'bytes': size})
    return rows
