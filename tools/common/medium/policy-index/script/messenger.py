from __future__ import annotations

import os
from pathlib import Path

DOC_EXTS = {'.md', '.txt', '.rst'}
IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor', 'generated',
}


def _path_key(path: Path) -> str:
    try:
        return str(path.resolve())
    except OSError:
        return str(path.absolute())


def discover_policy_files(paths: list[str]) -> tuple[list[Path], list[str], list[str], int]:
    files: list[Path] = []
    seen: set[str] = set()
    missing: list[str] = []
    unsupported: list[str] = []
    walk_error_count = 0

    def add_file(path: Path) -> None:
        if path.suffix.lower() not in DOC_EXTS:
            return
        key = _path_key(path)
        if key in seen:
            return
        seen.add(key)
        files.append(path)

    def on_walk_error(_error: OSError) -> None:
        nonlocal walk_error_count
        walk_error_count += 1

    for raw in paths:
        path = Path(raw)
        if not path.exists():
            missing.append(raw)
            continue
        if path.is_file():
            if path.suffix.lower() in DOC_EXTS:
                add_file(path)
            else:
                unsupported.append(raw)
            continue
        if not path.is_dir():
            unsupported.append(raw)
            continue

        for current, dirs, names in os.walk(path, onerror=on_walk_error):
            dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE_DIRS)
            current_path = Path(current)
            for name in sorted(names):
                add_file(current_path / name)

    files.sort(key=lambda item: item.as_posix())
    return files, missing, unsupported, walk_error_count


def read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError:
        return None
