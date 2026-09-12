#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


def changed(root, base):
    cmd = ['git', '-C', str(root), 'diff', '--name-only', base] if base else ['git', '-C', str(root), 'diff', '--name-only', 'HEAD']
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return []
    return [x.strip() for x in r.stdout.splitlines() if x.strip()]


def candidates(root, rel):
    p = Path(rel)
    stem = p.stem.lower().removeprefix('test_').removesuffix('_test')
    tests, docs = [], []
    for q in root.rglob('*'):
        if not q.is_file():
            continue
        name = q.name.lower()
        if stem and stem in name:
            rr = str(q.relative_to(root))
            if 'test' in name or 'tests' in {x.lower() for x in q.parts}:
                tests.append(rr)
            elif q.suffix.lower() in {'.md', '.rst', '.txt'}:
                docs.append(rr)
    return tests[:8], docs[:8]


def main():
    ap = argparse.ArgumentParser(description='Route changed files to likely tests and docs.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--base')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    rows = []
    for rel in changed(root, args.base):
        tests, docs = candidates(root, rel)
        rows.append({'changed': rel, 'tests': tests, 'docs': docs})
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            print(row['changed'])
            if row['tests']:
                print('  tests: ' + ', '.join(row['tests']))
            if row['docs']:
                print('  docs: ' + ', '.join(row['docs']))

if __name__ == '__main__':
    main()
