#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

IGNORE = {
    '.git', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist',
    '__pycache__', '.godot', 'vendor', 'generated'
}
CODE = {'.py', '.cs', '.go', '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh', '.gd', '.rs', '.java', '.js', '.ts'}


def main():
    parser = argparse.ArgumentParser(description='Generate a bounded Responsibility Map starter table without inventing semantic responsibilities.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--max', type=int, default=120, help='maximum rows printed')
    parser.add_argument('--max-scan-files', type=int, default=15000, help='maximum code files inspected')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rows = []
    scanned = 0
    truncated = False

    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        for name in sorted(files):
            path = Path(current) / name
            if path.suffix.lower() not in CODE:
                continue
            scanned += 1
            if scanned > args.max_scan_files:
                truncated = True
                break
            try:
                size = path.stat().st_size
            except OSError:
                size = 0
            rows.append((size, path.relative_to(root).as_posix()))
        if truncated:
            break

    rows.sort(reverse=True)
    print('| Path | Size | Responsibility |')
    print('|---|---:|---|')
    for size, path in rows[:args.max]:
        print(f'| `{path}` | {size} | TODO: describe ownership in one short sentence |')

    hidden = max(0, len(rows) - args.max)
    if hidden:
        print(f'\n<!-- output truncated: {hidden} more scanned code files -->')
    if truncated:
        print(f'<!-- scan truncated at {args.max_scan_files} code files; narrow root before increasing the scan budget -->')


if __name__ == '__main__':
    main()
