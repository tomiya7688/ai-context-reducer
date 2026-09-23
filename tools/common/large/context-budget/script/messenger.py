from __future__ import annotations

import os
from pathlib import Path

IGNORE = {'.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist', '__pycache__', '.godot', '.idea', '.vs', 'vendor'}
TEXT = {'.py', '.cs', '.go', '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh', '.gd', '.md', '.txt', '.rst', '.json', '.yaml', '.yml', '.toml', '.xml', '.ini'}


# 依存物や生成物を避けつつ、budget計測対象のtext fileを決定論的に列挙する。
def iter_text_files(root: Path, include_ignored: bool, stats: dict[str, int] | None = None):
    # walk失敗を握り潰さずwarningとして保持し、不完全な計測をclean扱いしない。
    def on_error(_error):
        if stats is not None:
            stats['walk_error_count'] = stats.get('walk_error_count', 0) + 1

    for current, dirs, files in os.walk(root, onerror=on_error):
        if not include_ignored:
            dirs[:] = [d for d in dirs if d.lower() not in IGNORE]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            if path.suffix.lower() in TEXT:
                yield path


# 読めないfileを空内容と混同せず、boundedなerror情報付きで返す。
def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return None


# size取得失敗を0 byteと誤認しないよう、値とerrorを分離して返す。
def file_size(path: Path) -> int | None:
    try:
        return path.stat().st_size
    except OSError:
        return None
