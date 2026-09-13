#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', 'bin', 'obj',
    'build', 'dist', '__pycache__', '.godot', '.idea', '.vs', 'vendor',
}
TEXT = {
    '.py', '.cs', '.go', '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh',
    '.gd', '.md', '.txt', '.rst', '.json', '.yaml', '.yml', '.toml', '.xml', '.ini',
}


def scan(root: Path, max_files: int):
    rows = []
    scanned = 0
    truncated = False

    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in IGNORE]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            if path.suffix.lower() not in TEXT:
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            scanned += 1
            estimated_tokens = max(1, size // 4)
            rows.append((estimated_tokens, size, path.relative_to(root).as_posix()))
            if scanned >= max_files:
                truncated = True
                return rows, scanned, truncated

    return rows, scanned, truncated


def main():
    parser = argparse.ArgumentParser(
        description='Estimate candidate context cost from file metadata without reading full contents.'
    )
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--top', type=int, default=40)
    parser.add_argument('--max-files', type=int, default=20000)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rows, scanned, truncated = scan(root, args.max_files)
    rows.sort(reverse=True)
    total = sum(row[0] for row in rows)

    print(f'estimated_total_tokens_if_all_candidates_read={total}')
    print(f'scanned_text_files={scanned}')
    print(f'truncated={str(truncated).lower()}')
    print('largest_candidates:')
    for tokens, size, path in rows[:args.top]:
        print(f'  {tokens:>8} tok~  {size:>10} bytes  {path}')
    if len(rows) > args.top:
        print(f'  ... {len(rows) - args.top} more indexed files')


if __name__ == '__main__':
    main()
