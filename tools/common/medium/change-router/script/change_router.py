#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from pathlib import Path

IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', 'vendor', '.godot', '.idea', '.vs'
}
DOC_EXTS = {'.md', '.rst', '.txt'}


def changed(root, base):
    cmd = ['git', '-C', str(root), 'diff', '--name-only', base] if base else [
        'git', '-C', str(root), 'diff', '--name-only', 'HEAD'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def build_index(root, max_files):
    entries = []
    truncated = False
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        for name in sorted(files):
            path = Path(current) / name
            rel = path.relative_to(root)
            entries.append((rel.as_posix(), name.lower(), {part.lower() for part in rel.parts}))
            if len(entries) >= max_files:
                truncated = True
                return entries, truncated
    return entries, truncated


def candidates(index, rel, per_kind):
    path = Path(rel)
    stem = path.stem.lower().removeprefix('test_').removesuffix('_test')
    if not stem:
        return [], []

    tests = []
    docs = []
    for indexed_rel, name, parts in index:
        if stem not in name:
            continue
        suffix = Path(indexed_rel).suffix.lower()
        if 'test' in name or 'tests' in parts or 'test' in parts:
            if len(tests) < per_kind:
                tests.append(indexed_rel)
        elif suffix in DOC_EXTS:
            if len(docs) < per_kind:
                docs.append(indexed_rel)
        if len(tests) >= per_kind and len(docs) >= per_kind:
            break
    return tests, docs


def main():
    parser = argparse.ArgumentParser(description='Route changed files to likely tests and docs using one bounded repository index.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--base')
    parser.add_argument('--max-changed', type=int, default=80)
    parser.add_argument('--max-index-files', type=int, default=12000)
    parser.add_argument('--per-kind', type=int, default=8)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    changed_files = changed(root, args.base)
    changed_truncated = len(changed_files) > args.max_changed
    changed_files = changed_files[:args.max_changed]

    index, index_truncated = build_index(root, args.max_index_files)
    rows = []
    for rel in changed_files:
        tests, docs = candidates(index, rel, args.per_kind)
        rows.append({'changed': rel, 'tests': tests, 'docs': docs})

    result = {
        'routes': rows,
        'index_files': len(index),
        'index_truncated': index_truncated,
        'changed_truncated': changed_truncated,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if index_truncated:
        print(f'[index truncated at {len(index)} files; use --max-index-files only if broader routing is required]')
    if changed_truncated:
        print(f'[changed files truncated at {args.max_changed}; narrow the diff or raise --max-changed intentionally]')
    for row in rows:
        print(row['changed'])
        if row['tests']:
            print('  tests: ' + ', '.join(row['tests']))
        if row['docs']:
            print('  docs: ' + ', '.join(row['docs']))


if __name__ == '__main__':
    main()
