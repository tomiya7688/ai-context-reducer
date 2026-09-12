#!/usr/bin/env python3
"""Bounded repository tree view using only the Python standard library."""
import argparse
from pathlib import Path

IGNORE = {'.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__', 'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs'}


def walk(path: Path, root: Path, depth: int, max_depth: int, budget: list[int]):
    if depth > max_depth or budget[0] <= 0:
        return
    try:
        children = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        return
    for child in children:
        if child.name in IGNORE:
            continue
        rel = child.relative_to(root).as_posix()
        print('  ' * depth + ('[D] ' if child.is_dir() else '[F] ') + rel)
        budget[0] -= 1
        if budget[0] <= 0:
            print('-- truncated --')
            return
        if child.is_dir():
            walk(child, root, depth + 1, max_depth, budget)


def main():
    ap = argparse.ArgumentParser(description='Portable bounded repository tree.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--max-depth', type=int, default=3)
    ap.add_argument('--max-entries', type=int, default=300)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    print(root.name + '/')
    walk(root, root, 1, args.max_depth, [args.max_entries])


if __name__ == '__main__':
    main()
