#!/usr/bin/env python3
"""Bounded repository tree view using only the Python standard library."""
import argparse
import json
from pathlib import Path

IGNORE = {'.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__', 'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs'}


# collect_tree は対象scopeを調べ、routingに必要な情報だけを集める。
def collect_tree(path: Path, root: Path, depth: int, max_depth: int, max_entries: int, state: dict[str, object]):
    if depth > max_depth or (max_entries > 0 and state['entries_scanned'] >= max_entries):
        return
    try:
        children = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        state['read_error_paths'].append(path.relative_to(root).as_posix() if path != root else '.')
        return
    for child in children:
        if child.name in IGNORE:
            continue
        if max_entries > 0 and state['entries_scanned'] >= max_entries:
            state['entries_truncated'] = True
            return
        rel = child.relative_to(root).as_posix()
        is_dir = child.is_dir()
        state['entries'].append({'path': rel, 'kind': 'directory' if is_dir else 'file', 'depth': depth})
        state['entries_scanned'] += 1
        if is_dir:
            collect_tree(child, root, depth + 1, max_depth, max_entries, state)
            if state['entries_truncated']:
                return


# build_tree は解析結果を後段で再利用できる構造へ組み立てる。
def build_tree(root: Path, max_depth: int, max_entries: int) -> dict[str, object]:
    state = {
        'entries': [],
        'entries_scanned': 0,
        'entries_truncated': False,
        'read_error_paths': [],
    }
    collect_tree(root, root, 1, max_depth, max_entries, state)
    return {
        'tool': 'tree-view',
        'status': 'ok',
        'project_root': str(root),
        'max_depth': max_depth,
        'max_entries': max_entries,
        **state,
    }


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    ap = argparse.ArgumentParser(description='Portable bounded repository tree as self-describing JSON.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--max-depth', type=int, default=3)
    ap.add_argument('--max-entries', type=int, default=300, help='Output limit. 0 means unlimited within max-depth.')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        result = {'tool': 'tree-view', 'status': 'input_missing', 'project_root': str(root)}
    elif not root.is_dir():
        result = {'tool': 'tree-view', 'status': 'input_not_directory', 'project_root': str(root)}
    else:
        result = build_tree(root, max(0, args.max_depth), max(0, args.max_entries))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
