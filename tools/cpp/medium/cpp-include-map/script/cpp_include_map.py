#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path

INCLUDE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]', re.M)
IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', 'vendor', '.idea', '.vs',
}
EXTENSIONS = {'.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx', '.h'}


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


def main():
    parser = argparse.ArgumentParser(description='Build a bounded C++ include map.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=1000)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files, truncated = source_files(root, args.limit)
    rows = []
    for path in files:
        text = path.read_text(encoding='utf-8', errors='ignore')
        rows.append({
            'file': path.relative_to(root).as_posix(),
            'includes': sorted(set(INCLUDE.findall(text))),
        })

    print(json.dumps({
        'root': root.name,
        'files': rows,
        'truncated': truncated,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
