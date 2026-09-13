#!/usr/bin/env python3
import argparse
import json
import os
from collections import Counter
from pathlib import Path

IGNORE = {'.git', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist', '__pycache__', 'vendor'}
LANG = {
    '.py': 'Python', '.cs': 'CSharp', '.go': 'Go', '.gd': 'GDScript',
    '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.hpp': 'C++', '.hh': 'C++', '.hxx': 'C++',
    '.c': 'C', '.h': 'C/C++ Header',
    '.rs': 'Rust', '.js': 'JavaScript', '.ts': 'TypeScript', '.java': 'Java'
}


def walk(root: Path, max_files: int):
    files = []
    truncated = False
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        for name in sorted(names):
            files.append(Path(current) / name)
            if len(files) >= max_files:
                truncated = True
                return files, truncated
    return files, truncated


def main():
    parser = argparse.ArgumentParser(description='Create a shallow bounded repository profile.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--max-files', type=int, default=20000)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files, truncated = walk(root, args.max_files)
    langs = Counter(LANG.get(path.suffix.lower(), 'Other') for path in files)
    code_files = sum(v for k, v in langs.items() if k != 'Other')

    if truncated:
        size = 'large-or-unknown'
    else:
        size = 'small' if len(files) < 200 else 'medium' if len(files) < 2000 else 'large'

    top_dirs = set()
    for path in files:
        rel = path.relative_to(root)
        if rel.parts:
            top_dirs.add(rel.parts[0])

    data = {
        'root': root.name,
        'files_scanned': len(files),
        'scan_truncated': truncated,
        'code_files_scanned': code_files,
        'project_size': size,
        'languages': dict(langs.most_common()),
        'top_dirs': sorted(top_dirs)[:30],
    }

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    suffix = ' scan_truncated=yes' if truncated else ''
    print(f"project={data['root']} size={size} files_scanned={len(files)} code_files_scanned={code_files}{suffix}")
    print('languages=' + ', '.join(f'{k}:{v}' for k, v in langs.most_common()))
    print('top_dirs=' + ', '.join(data['top_dirs']))
    if truncated:
        print('note=profile is intentionally bounded; raise --max-files only when broader evidence is required')


if __name__ == '__main__':
    main()
