#!/usr/bin/env python3
"""Small dependency-free path finder, similar to the subset of fd we need."""
import argparse
import fnmatch
from pathlib import Path

IGNORE = {'.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__', 'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs'}


def main():
    ap = argparse.ArgumentParser(description='Portable bounded path finder fallback.')
    ap.add_argument('pattern', nargs='?', default='*')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--type', choices=['file', 'dir', 'any'], default='file')
    ap.add_argument('--max-results', type=int, default=200)
    ap.add_argument('--max-depth', type=int, default=20)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    count = 0
    for p in root.rglob('*'):
        rel = p.relative_to(root)
        if len(rel.parts) > args.max_depth or any(part in IGNORE for part in rel.parts):
            continue
        if args.type == 'file' and not p.is_file():
            continue
        if args.type == 'dir' and not p.is_dir():
            continue
        if not fnmatch.fnmatch(p.name, args.pattern) and not fnmatch.fnmatch(rel.as_posix(), args.pattern):
            continue
        print(rel.as_posix())
        count += 1
        if count >= args.max_results:
            print(f'-- truncated after {count} results --')
            return


if __name__ == '__main__':
    main()
