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


# role はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def role(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    low = '/'.join(part.lower() for part in path.parts)
    if 'test' in path.name.lower() or 'tests' in parts or 'test' in parts:
        return 'tests'
    if path.suffix.lower() in {'.md', '.rst', '.txt'} or 'docs' in parts or 'doc' in parts:
        return 'documentation'
    if path.suffix.lower() in {'.py', '.cs', '.go', '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh', '.gd', '.rs', '.java', '.js', '.ts'}:
        return 'source'
    if path.suffix.lower() in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.xml'}:
        return 'configuration'
    if path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.wav', '.mp3', '.ogg', '.mp4', '.zip', '.7z'}:
        return 'asset_or_binary'
    return 'other'


# build_role_map は解析結果を後段で再利用できる構造へ組み立てる。
def build_role_map(root: Path, max_files: int, example_limit: int) -> dict[str, object]:
    groups = defaultdict(lambda: {'file_count': 0, 'example_paths': []})
    scanned = 0
    truncated = False

    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in SKIP)
        for name in sorted(files):
            if max_files > 0 and scanned >= max_files:
                truncated = True
                break
            scanned += 1
            rel = (Path(current) / name).relative_to(root)
            group = groups[role(rel)]
            group['file_count'] += 1
            if example_limit == 0 or len(group['example_paths']) < example_limit:
                group['example_paths'].append(rel.as_posix())
        if truncated:
            break

    roles = {}
    for key, value in sorted(groups.items()):
        paths = value['example_paths']
        roles[key] = {
            'file_count': value['file_count'],
            'example_paths': paths,
            'example_paths_truncated': example_limit > 0 and value['file_count'] > len(paths),
        }

    return {
        'tool': 'file-role-map',
        'status': 'ok',
        'project_root': str(root),
        'files_scanned': scanned,
        'scan_truncated': truncated,
        'roles': roles,
    }


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    parser = argparse.ArgumentParser(description='Classify repository files by likely context role as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--max-files', type=int, default=0, help='Optional safety limit. 0 means unlimited.')
    parser.add_argument('--examples', type=int, default=12, help='Example paths per role. 0 means unlimited.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        result = {'tool': 'file-role-map', 'status': 'input_missing', 'project_root': str(root)}
    elif not root.is_dir():
        result = {'tool': 'file-role-map', 'status': 'input_not_directory', 'project_root': str(root)}
    else:
        result = build_role_map(root, args.max_files, max(0, args.examples))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
