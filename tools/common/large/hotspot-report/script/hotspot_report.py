#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

SKIP = {
    '.git', '.hg', '.svn', 'node_modules', 'build', 'dist', 'bin', 'obj',
    '.venv', 'venv', '__pycache__', '.godot', '.idea', '.vs', 'vendor',
}


def main():
    parser = argparse.ArgumentParser(description='Report large/deep repository hotspots with bounded traversal.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=30)
    parser.add_argument('--max-files', type=int, default=50000)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rows = []
    scanned = 0
    truncated = False

    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            try:
                size = path.stat().st_size
            except OSError:
                continue
            rel = path.relative_to(root)
            rows.append((size, len(rel.parts), rel.as_posix()))
            scanned += 1
            if scanned >= args.max_files:
                truncated = True
                break
        if truncated:
            break

    print(f'scanned_files={scanned} truncated={str(truncated).lower()}')
    for size, depth, name in sorted(rows, reverse=True)[:args.limit]:
        print(f'{size:>10} bytes depth={depth} {name}')


if __name__ == '__main__':
    main()
