#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path

TOOL = 'gdscript-dependency-map'
LOAD = re.compile(r'(?:load|preload)\(\s*["\']([^"\']+)["\']\s*\)')
EXTENDS = re.compile(r'^\s*extends\s+["\']([^"\']+)["\']', re.M)
IGNORE_DIRS = {'.git', '.godot', 'build', 'dist', '.idea', '.vs'}


# GDScript sourceだけを決定論的に列挙し、依存物や生成物を通常contextから外す。
def source_files(root: Path):
    found = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE_DIRS)
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            if path.suffix.lower() == '.gd':
                found.append(path)
    return found


# GDScript依存をbounded mapへ集約し、truncationとparse失敗を完全性signalとして残す。
def build_result(root: Path, limit: int):
    all_files = source_files(root)
    limit = max(0, limit)
    truncated = limit > 0 and len(all_files) > limit
    selected = all_files[:limit] if limit > 0 else all_files
    rows = []
    read_errors = 0
    dependency_count = 0
    for path in selected:
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
            dependencies = set(LOAD.findall(text))
            dependencies.update(EXTENDS.findall(text))
            dependencies = sorted(dependencies)
            status = 'ok'
            error = None
        except OSError as exc:
            dependencies = []
            status = 'read_failed'
            error = str(exc)
            read_errors += 1
        dependency_count += len(dependencies)
        row = {'file': path.relative_to(root).as_posix(), 'status': status, 'dependencies': dependencies}
        if error:
            row['error'] = error
        rows.append(row)
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if read_errors or truncated else 'ok',
        'language': 'gdscript',
        'root_path': str(root),
        'files': rows,
        'file_count_total': len(all_files),
        'files_returned': len(rows),
        'dependencies_returned': dependency_count,
        'read_error_count': read_errors,
        'scan_truncated': truncated,
    }


# CLI入力を検証し、正常結果と失敗状態を同じ機械可読JSON契約で返す。
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
