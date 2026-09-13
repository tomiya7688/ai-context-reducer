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
            if max_files > 0 and len(files) >= max_files:
                truncated = True
                return files, truncated
    return files, truncated


def build_profile(root: Path, max_files: int) -> dict[str, object]:
    files, truncated = walk(root, max_files)
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

    return {
        'tool': 'repo-profile',
        'status': 'ok',
        'project_root': str(root),
        'project_size_class': size,
        'files_scanned': len(files),
        'scan_truncated': truncated,
        'code_files_scanned': code_files,
        'language_file_counts': dict(langs.most_common()),
        'top_level_entries': sorted(top_dirs)[:30],
        'top_level_entries_truncated': len(top_dirs) > 30,
    }


def main():
    parser = argparse.ArgumentParser(description='Create a shallow repository profile as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--max-files', type=int, default=0, help='Optional safety limit. 0 means unlimited.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        result = {'tool': 'repo-profile', 'status': 'input_missing', 'project_root': str(root)}
    elif not root.is_dir():
        result = {'tool': 'repo-profile', 'status': 'input_not_directory', 'project_root': str(root)}
    else:
        result = build_profile(root, args.max_files)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
