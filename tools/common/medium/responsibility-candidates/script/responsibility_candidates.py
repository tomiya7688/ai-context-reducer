#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', 'bin', 'obj',
    'build', 'dist', '__pycache__', '.godot', '.idea', '.vs', 'vendor', 'generated'
}
CODE = {'.py', '.cs', '.go', '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh', '.gd', '.rs', '.java', '.js', '.ts'}


def scan_candidates(root: Path, max_scan_files: int = 0):
    rows: list[tuple[int | None, str]] = []
    scanned = 0
    scan_truncated = False
    stat_error_count = 0
    walk_error_count = 0

    def on_walk_error(_error: OSError) -> None:
        nonlocal walk_error_count
        walk_error_count += 1

    for current, dirs, files in os.walk(root, onerror=on_walk_error):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        for name in sorted(files):
            path = Path(current) / name
            if path.suffix.lower() not in CODE:
                continue
            if max_scan_files > 0 and scanned >= max_scan_files:
                scan_truncated = True
                return rows, scanned, scan_truncated, stat_error_count, walk_error_count
            scanned += 1
            try:
                size: int | None = path.stat().st_size
            except OSError:
                size = None
                stat_error_count += 1
            rows.append((size, path.relative_to(root).as_posix()))
    return rows, scanned, scan_truncated, stat_error_count, walk_error_count


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a bounded Responsibility Map starter table without inventing semantic responsibilities.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--max', type=int, default=120, help='maximum rows printed; 0 prints no candidate rows')
    parser.add_argument('--max-scan-files', type=int, default=0, help='optional safety limit for inspected code files; 0 means unlimited')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f'responsibility-candidates: input_missing: {root}', file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f'responsibility-candidates: input_not_directory: {root}', file=sys.stderr)
        return 2

    max_rows = max(0, args.max)
    max_scan_files = max(0, args.max_scan_files)
    rows, scanned, scan_truncated, stat_errors, walk_errors = scan_candidates(root, max_scan_files)
    rows.sort(key=lambda row: (row[0] is not None, row[0] or -1, row[1]), reverse=True)

    print('| Path | Size | Responsibility |')
    print('|---|---:|---|')
    for size, path in rows[:max_rows] if max_rows > 0 else []:
        size_text = str(size) if size is not None else 'unavailable'
        print(f'| `{path}` | {size_text} | TODO: describe ownership in one short sentence |')

    hidden = len(rows) - min(len(rows), max_rows)
    if hidden:
        print(f'\n<!-- output truncated: {hidden} more scanned code files -->')
    if stat_errors:
        print(f'<!-- stat warnings: {stat_errors} code files had unavailable size metadata -->')
    if walk_errors:
        print(f'<!-- walk warnings: {walk_errors} filesystem entries could not be visited -->')
    if scan_truncated:
        print(f'<!-- scan truncated at {max_scan_files} code files by explicit safety limit -->')
    print(f'<!-- scanned code files: {scanned} -->')
    return 0


if __name__ == '__main__':
    sys.exit(main())
