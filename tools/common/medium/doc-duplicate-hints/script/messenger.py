from __future__ import annotations

from pathlib import Path

DOC_EXTS = {'.md', '.txt', '.rst'}


def iter_documents(root: Path):
    for path in root.rglob('*'):
        if path.is_file() and path.suffix.lower() in DOC_EXTS:
            yield path


def read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError:
        return None
