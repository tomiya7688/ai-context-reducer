from __future__ import annotations

import os
import subprocess
from pathlib import Path

IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor',
}
DOC_EXTS = {'.md', '.rst', '.txt'}
TEST_DIRS = {'test', 'tests', 'spec', 'specs'}


def changed_files(root: Path, base: str | None) -> dict[str, object]:
    cmd = ['git', '-C', str(root), 'diff', '--name-only', base or 'HEAD']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError:
        return {'ok': False, 'lines': [], 'error_kind': 'git_unavailable'}
    if result.returncode != 0:
        return {'ok': False, 'lines': [], 'error_kind': 'git_query_failed'}
    return {
        'ok': True,
        'lines': [line.strip() for line in result.stdout.splitlines() if line.strip()],
        'error_kind': None,
    }


def is_test_candidate(path: Path, rel_parts: set[str]) -> bool:
    if rel_parts & TEST_DIRS:
        return True
    name = path.name.lower()
    stem = path.stem.lower()
    return (
        stem.startswith(('test_', 'test-', 'spec_', 'spec-'))
        or stem.endswith(('_test', '-test', '_spec', '-spec'))
        or '.test.' in name
        or '.spec.' in name
    )


def candidate_index(root: Path, max_files: int) -> tuple[list[dict[str, object]], bool, int]:
    rows: list[dict[str, object]] = []
    truncated = False
    walk_error_count = 0

    def on_walk_error(_error: OSError) -> None:
        nonlocal walk_error_count
        walk_error_count += 1

    for current, dirs, files in os.walk(root, onerror=on_walk_error):
        dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]
        current_path = Path(current)
        rel_dir = current_path.relative_to(root)
        rel_parts = {part.lower() for part in rel_dir.parts}

        for name in files:
            path = current_path / name
            rel = path.relative_to(root).as_posix()
            low_name = name.lower()
            suffix = path.suffix.lower()
            is_test = is_test_candidate(path, rel_parts)
            is_doc = suffix in DOC_EXTS
            if not is_test and not is_doc:
                continue

            if max_files > 0 and len(rows) >= max_files:
                truncated = True
                return rows, truncated, walk_error_count
            rows.append({
                'path': rel,
                'name': low_name,
                'is_test': is_test,
                'is_doc': is_doc,
            })

    return rows, truncated, walk_error_count
