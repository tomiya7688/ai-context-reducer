#!/usr/bin/env python3
import argparse
import ast
import json
import os
from pathlib import Path

TOOL = 'python-module-graph'
IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', 'vendor', '.idea', '.vs',
}


def module_name(root: Path, path: Path):
    rel = path.relative_to(root).with_suffix('')
    parts = list(rel.parts)
    if parts and parts[-1] == '__init__':
        parts.pop()
    return '.'.join(parts)


def dependencies(path: Path):
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        return 'read_failed', [], str(exc)
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return 'parse_failed', [], str(exc)
    deps = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            deps.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            deps.add(node.module)
    return 'ok', sorted(deps), None


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
    files = all_files[:limit] if limit > 0 else all_files
    modules = {module_name(root, path) for path in files}
    edges = []
    parse_errors = 0
    read_errors = 0
    for path in files:
        source = module_name(root, path)
        status, deps, _ = dependencies(path)
        parse_errors += status == 'parse_failed'
        read_errors += status == 'read_failed'
        for dep in deps:
            matches = [module for module in modules if module == dep or module.startswith(dep + '.') or dep.startswith(module + '.')]
            if matches:
                edges.append({'from': source, 'to': sorted(matches, key=lambda value: (len(value), value))[0]})
    edges = sorted({(edge['from'], edge['to']) for edge in edges})
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if parse_errors or read_errors or truncated else 'ok',
        'language': 'python',
        'root_path': str(root),
        'module_count': len(modules),
        'edges': [{'from': source, 'to': target} for source, target in edges],
        'edge_count': len(edges),
        'files_scanned': len(files),
        'file_count_total': len(all_files),
        'parse_error_count': parse_errors,
        'read_error_count': read_errors,
        'scan_truncated': truncated,
    }


def main():
    parser = argparse.ArgumentParser()
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
