from __future__ import annotations

from pathlib import Path

DOC_EXTS = {'.md', '.txt', '.rst'}


def iter_policy_files(paths: list[str]):
    for raw in paths:
        path = Path(raw)
        if path.is_file():
            yield path
            continue
        for child in path.rglob('*'):
            if child.is_file() and child.suffix.lower() in DOC_EXTS:
                yield child


def read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError:
        return None
