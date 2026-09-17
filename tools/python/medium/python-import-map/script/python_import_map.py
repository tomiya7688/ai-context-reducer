#!/usr/bin/env python3
import argparse
import ast
import json
import os
from pathlib import Path

TOOL = 'python-import-map'
IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', 'vendor', '.idea', '.vs',
}


def file_imports(path: Path):
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        return {'status': 'read_failed', 'imports': [], 'error': str(exc)}
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {'status': 'parse_failed', 'imports': [], 'error': str(exc)}
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add('.' * node.level + (node.module or ''))
    return {'status': 'ok', 'imports': sorted(imports)}


def source_files(root: Path):
    found = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE_DIRS)
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            if path.suffix.lower() == '.py':
                found.append(path)
    return found


def build_result(root: Path, limit: int):
    all_files = source_files(root)
    limit = max(0, limit)
    truncated = limit > 0 and len(all_files) > limit
    selected = all_files[:limit] if limit > 0 else all_files
    rows = []
    parse_errors = 0
    read_errors = 0
    import_count = 0
    for path in selected:
        result = file_imports(path)
        parse_errors += result['status'] == 'parse_failed'
        read_errors += result['status'] == 'read_failed'
        import_count += len(result['imports'])
        row = {
            'file': path.relative_to(root).as_posix(),
            'status': result['status'],
            'imports': result['imports'],
        }
        if 'error' in result:
            row['error'] = result['error']
        rows.append(row)
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if parse_errors or read_errors or truncated else 'ok',
        'language': 'python',
        'root_path': str(root),
        'files': rows,
        'file_count_total': len(all_files),
        'files_returned': len(rows),
        'imports_returned': import_count,
        'parse_error_count': parse_errors,
        'read_error_count': read_errors,
        'scan_truncated': truncated,
    }


def main():
    parser = argparse.ArgumentParser()
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
