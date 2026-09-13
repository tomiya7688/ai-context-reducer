from __future__ import annotations

import os
from pathlib import Path

IGNORE = {'.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist', '__pycache__', '.godot', '.idea', '.vs', 'vendor'}
TEXT = {'.py', '.cs', '.go', '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh', '.gd', '.md', '.txt', '.rst', '.json', '.yaml', '.yml', '.toml', '.xml', '.ini'}


def iter_text_files(root: Path, include_ignored: bool):
    for current, dirs, files in os.walk(root):
        if not include_ignored:
            dirs[:] = [d for d in dirs if d.lower() not in IGNORE]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            if path.suffix.lower() in TEXT:
                yield path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return None


def file_size(path: Path) -> int | None:
    try:
        return path.stat().st_size
    except OSError:
        return None
