#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path

INCLUDE = re.compile(r'^\s*#\s*include\s*"([^"]+)"', re.M)
IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', 'vendor', '.idea', '.vs',
}
EXTENSIONS = {'.c', '.h'}


def source_files(root: Path, limit: int):
    found = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            if path.suffix.lower() not in EXTENSIONS:
                continue
            found.append(path)
            if len(found) >= limit:
                return found, True
    return found, False


def build_edges(root: Path, files: list[Path]):
    relmap = {path.relative_to(root).as_posix(): path for path in files}
    byname = {path.name: rel for rel, path in relmap.items()}
    edges = []

    for rel, path in relmap.items():
        text = path.read_text(encoding='utf-8', errors='ignore')
        for include in INCLUDE.findall(text):
            target = include if include in relmap else byname.get(Path(include).name)
            if target:
                edges.append({'from': rel, 'to': target})
    return edges


def main():
    parser = argparse.ArgumentParser(description='Build a bounded local C include graph.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=1500)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files, truncated = source_files(root, args.limit)
    edges = build_edges(root, files)

    print(json.dumps({
        'root': root.name,
        'files': len(files),
        'edges': edges,
        'truncated': truncated,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
