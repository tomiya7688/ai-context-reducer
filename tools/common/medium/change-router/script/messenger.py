from __future__ import annotations

import os
import subprocess
from pathlib import Path

IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor',
}
DOC_EXTS = {'.md', '.rst', '.txt'}


def changed_files(root: Path, base: str | None) -> tuple[bool, list[str]]:
    cmd = ['git', '-C', str(root), 'diff', '--name-only', base or 'HEAD']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, []
    return True, [line.strip() for line in result.stdout.splitlines() if line.strip()]


def candidate_index(root: Path, max_files: int) -> tuple[list[dict[str, object]], bool]:
    rows: list[dict[str, object]] = []
    truncated = False

    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]
        current_path = Path(current)
        rel_dir = current_path.relative_to(root)
        rel_parts = {part.lower() for part in rel_dir.parts}

        for name in files:
            path = current_path / name
            rel = path.relative_to(root).as_posix()
            low_name = name.lower()
            suffix = path.suffix.lower()
            is_test = 'test' in low_name or 'test' in rel_parts or 'tests' in rel_parts
            is_doc = suffix in DOC_EXTS
            if not is_test and not is_doc:
                continue

            rows.append({
                'path': rel,
                'name': low_name,
                'is_test': is_test,
                'is_doc': is_doc,
            })
            if max_files > 0 and len(rows) >= max_files:
                truncated = True
                return rows, truncated

    return rows, truncated
