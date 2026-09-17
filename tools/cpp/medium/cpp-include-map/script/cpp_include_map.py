#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path

TOOL = 'cpp-include-map'
INCLUDE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]', re.M)
IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', 'vendor', '.idea', '.vs',
}
EXTENSIONS = {'.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx', '.h'}


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
    selected = all_files[:limit] if limit > 0 else all_files
    rows = []
    read_errors = 0
    include_count = 0
    for path in selected:
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
            includes = sorted(set(INCLUDE.findall(text)))
            status = 'ok'
            error = None
        except OSError as exc:
            includes = []
            status = 'read_failed'
            error = str(exc)
            read_errors += 1
        include_count += len(includes)
        row = {'file': path.relative_to(root).as_posix(), 'status': status, 'includes': includes}
        if error:
            row['error'] = error
        rows.append(row)
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if read_errors or truncated else 'ok',
        'language': 'cpp',
        'root_path': str(root),
        'files': rows,
        'file_count_total': len(all_files),
        'files_returned': len(rows),
        'includes_returned': include_count,
        'read_error_count': read_errors,
        'scan_truncated': truncated,
    }


def main():
    parser = argparse.ArgumentParser(description='Build a C++ include map.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=0, help='maximum files to return; 0 means unlimited')
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
