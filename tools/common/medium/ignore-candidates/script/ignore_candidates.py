#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

NAMES = {'build', 'dist', 'bin', 'obj', '.cache', 'cache', '.godot', 'node_modules', '.venv', 'venv', 'coverage', 'logs', 'log', 'tmp', 'temp', 'backups', 'backup'}
EXTS = {'.log', '.tmp', '.bak', '.cache', '.pyc', '.pdb', '.dll', '.so', '.dylib', '.exe', '.class', '.jar', '.zip', '.7z'}


def scan_candidates(root: Path) -> tuple[list[dict[str, str]], int]:
    candidates: list[dict[str, str]] = []
    walk_error_count = 0

    def on_walk_error(_error: OSError) -> None:
        nonlocal walk_error_count
        walk_error_count += 1

    for current, dirs, files in os.walk(root, onerror=on_walk_error):
        current_path = Path(current)
        kept_dirs = []
        for name in sorted(dirs):
            path = current_path / name
            if name.lower() in NAMES:
                candidates.append({
                    'path': path.relative_to(root).as_posix(),
                    'kind': 'directory',
                    'matched_rule': f'directory_name:{name.lower()}',
                })
            else:
                kept_dirs.append(name)
        dirs[:] = kept_dirs

        for name in sorted(files):
            path = current_path / name
            suffix = path.suffix.lower()
            if suffix in EXTS:
                candidates.append({
                    'path': path.relative_to(root).as_posix(),
                    'kind': 'file',
                    'matched_rule': f'file_extension:{suffix}',
                })

    candidates.sort(key=lambda item: item['path'])
    return candidates, walk_error_count


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description='Suggest likely low-value context paths as self-describing JSON. Review before adding ignore rules.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=80, help='Maximum candidates returned. 0 means unlimited.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        emit({'tool': 'ignore-candidates', 'status': 'input_missing', 'root_path': str(root)})
        return 2
    if not root.is_dir():
        emit({'tool': 'ignore-candidates', 'status': 'input_not_directory', 'root_path': str(root)})
        return 2

    all_candidates, walk_error_count = scan_candidates(root)
    limit = max(0, args.limit)
    candidates = all_candidates if limit == 0 else all_candidates[:limit]
    emit({
        'tool': 'ignore-candidates',
        'status': 'ok_with_warnings' if walk_error_count else 'ok',
        'root_path': str(root),
        'candidate_count_total': len(all_candidates),
        'candidates': candidates,
        'candidates_truncated': len(candidates) < len(all_candidates),
        'walk_error_count': walk_error_count,
        'review_required_before_ignoring': True,
    })
    return 0


if __name__ == '__main__':
    sys.exit(main())
