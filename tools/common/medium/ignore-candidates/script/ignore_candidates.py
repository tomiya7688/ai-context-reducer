#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

NAMES = {'build', 'dist', 'bin', 'obj', '.cache', 'cache', '.godot', 'node_modules', '.venv', 'venv', 'coverage', 'logs', 'log', 'tmp', 'temp', 'backups', 'backup'}
EXTS = {'.log', '.tmp', '.bak', '.cache', '.pyc', '.pdb', '.dll', '.so', '.dylib', '.exe', '.class', '.jar', '.zip', '.7z'}


def main():
    parser = argparse.ArgumentParser(description='Suggest likely low-value context paths as self-describing JSON. Review before adding ignore rules.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=80)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(json.dumps({
            'tool': 'ignore-candidates',
            'status': 'root_missing',
            'root': str(root),
        }, ensure_ascii=False, indent=2))
        return

    found = set()
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        parts = {part.lower() for part in rel.parts}
        if parts & NAMES or (path.is_file() and path.suffix.lower() in EXTS):
            found.add(rel.as_posix())

    candidates = sorted(found)
    print(json.dumps({
        'tool': 'ignore-candidates',
        'status': 'ok',
        'root': str(root),
        'candidate_count': len(candidates),
        'candidates': candidates[:args.limit],
        'candidates_truncated': len(candidates) > args.limit,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
