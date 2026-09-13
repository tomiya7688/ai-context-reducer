#!/usr/bin/env python3
import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

SKIP = {
    '.git', '.venv', 'venv', 'node_modules', '__pycache__',
    'build', 'dist', 'bin', 'obj', 'cache', 'generated', 'vendor'
}


def role(path):
    low = '/'.join(part.lower() for part in path.parts)
    if path.suffix.lower() in {'.md', '.rst', '.txt'} or 'docs/' in low or 'doc/' in low:
        return 'docs'
    if 'test' in path.name.lower() or '/tests/' in low or '/test/' in low:
        return 'tests'
    if path.suffix.lower() in {'.py', '.cs', '.go', '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh', '.gd', '.rs', '.java', '.js', '.ts'}:
        return 'source'
    if path.suffix.lower() in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.xml'}:
        return 'config'
    if path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.wav', '.mp3', '.ogg', '.mp4', '.zip', '.7z'}:
        return 'asset/binary'
    return 'other'


def main():
    parser = argparse.ArgumentParser(description='Classify repository files by likely context role using a bounded scan.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--max-files', type=int, default=15000)
    parser.add_argument('--examples', type=int, default=12)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    groups = defaultdict(lambda: {'count': 0, 'examples': []})
    scanned = 0
    truncated = False

    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in SKIP)
        for name in sorted(files):
            scanned += 1
            if scanned > args.max_files:
                truncated = True
                break
            rel = (Path(current) / name).relative_to(root)
            group = groups[role(rel)]
            group['count'] += 1
            if len(group['examples']) < args.examples:
                group['examples'].append(rel.as_posix())
        if truncated:
            break

    data = {
        'roles': {key: value for key, value in sorted(groups.items())},
        'files_scanned': min(scanned, args.max_files),
        'scan_truncated': truncated,
    }

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if truncated:
        print(f'[scan truncated at {args.max_files} files; narrow root or raise --max-files intentionally]')
    for key, value in data['roles'].items():
        print(f"{key}: {value['count']}")
        for example in value['examples']:
            print(f'  - {example}')


if __name__ == '__main__':
    main()
