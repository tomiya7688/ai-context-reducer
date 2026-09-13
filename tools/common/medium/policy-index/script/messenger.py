from __future__ import annotations

from pathlib import Path

DOC_EXTS = {'.md', '.txt', '.rst'}


def discover_policy_files(paths: list[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    missing: list[str] = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            missing.append(raw)
            continue
        if path.is_file():
            if path.suffix.lower() in DOC_EXTS:
                files.append(path)
            continue
        files.extend(
            child for child in path.rglob('*')
            if child.is_file() and child.suffix.lower() in DOC_EXTS
        )
    return files, missing


def read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError:
        return None
