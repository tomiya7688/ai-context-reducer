#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path

TOOL = 'c-include-graph'
INCLUDE = re.compile(r'^\s*#\s*include\s*"([^"]+)"', re.M)
IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', 'vendor', '.idea', '.vs',
}
EXTENSIONS = {'.c', '.h'}


def source_files(root: Path):
    found = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE_DIRS)
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            if path.suffix.lower() in EXTENSIONS:
                found.append(path)
    return found


def build_result(root: Path, limit: int):
    all_files = source_files(root)
    limit = max(0, limit)
    truncated = limit > 0 and len(all_files) > limit
    files = all_files[:limit] if limit > 0 else all_files
    relmap = {path.relative_to(root).as_posix(): path for path in files}
    byname = {path.name: rel for rel, path in relmap.items()}
    edges = set()
    read_errors = 0
    for rel, path in relmap.items():
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            read_errors += 1
            continue
        for include in INCLUDE.findall(text):
            target = include if include in relmap else byname.get(Path(include).name)
            if target:
                edges.add((rel, target))
    edge_rows = [{'from': source, 'to': target} for source, target in sorted(edges)]
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if read_errors or truncated else 'ok',
        'language': 'c',
        'root_path': str(root),
        'file_count_total': len(all_files),
        'files_scanned': len(files),
        'edges': edge_rows,
        'edge_count': len(edge_rows),
        'read_error_count': read_errors,
        'scan_truncated': truncated,
    }


def main():
    parser = argparse.ArgumentParser(description='Build a local C include graph.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=0, help='maximum source files to analyze; 0 means unlimited')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(json.dumps({'tool': TOOL, 'status': 'input_missing', 'root_path': str(root)}, indent=2))
        raise SystemExit(2)
    if not root.is_dir():
        print(json.dumps({'tool': TOOL, 'status': 'input_not_directory', 'root_path': str(root)}, indent=2))
        raise SystemExit(2)
    print(json.dumps(build_result(root, args.limit), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
