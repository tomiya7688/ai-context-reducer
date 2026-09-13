#!/usr/bin/env python3
"""Small dependency-free path finder, similar to the subset of fd we need."""
import argparse
import fnmatch
import os
from pathlib import Path

IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor'
}


def main():
    parser = argparse.ArgumentParser(description='Portable bounded path finder fallback.')
    parser.add_argument('pattern', nargs='?', default='*')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--type', choices=['file', 'dir', 'any'], default='file')
    parser.add_argument('--max-results', type=int, default=200)
    parser.add_argument('--max-depth', type=int, default=20)
    parser.add_argument('--max-visited', type=int, default=20000)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    matched = 0
    visited = 0

    for current, dirs, files in os.walk(root):
        rel_dir = Path(current).relative_to(root)
        depth = 0 if rel_dir == Path('.') else len(rel_dir.parts)
        dirs[:] = sorted(
            d for d in dirs
            if d.lower() not in IGNORE and depth < args.max_depth
        )

        names = []
        if args.type in {'dir', 'any'}:
            names.extend((name, True) for name in dirs)
        if args.type in {'file', 'any'}:
            names.extend((name, False) for name in sorted(files))

        for name, is_dir in names:
            visited += 1
            if visited > args.max_visited:
                print(f'-- scan truncated after {args.max_visited} visited entries --')
                return

            path = Path(current) / name
            rel = path.relative_to(root)
            if len(rel.parts) > args.max_depth:
                continue
            if not fnmatch.fnmatch(name, args.pattern) and not fnmatch.fnmatch(rel.as_posix(), args.pattern):
                continue

            print(rel.as_posix() + ('/' if is_dir else ''))
            matched += 1
            if matched >= args.max_results:
                print(f'-- truncated after {matched} results --')
                return


if __name__ == '__main__':
    main()
