#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def classify(path):
    p = path.lower()
    out = []
    if any(x in p for x in ('ui', 'view', 'scene', 'widget', 'layout', '.gd')):
        out += ['headless smoke if possible', 'visual confirmation when acceptance is visual']
    if any(x in p for x in ('package', 'installer', 'publish', 'release', 'dist')):
        out += ['artifact generation', 'artifact smoke']
    if any(x in p for x in ('parser', 'lexer', 'rule', 'validator', 'protocol')):
        out += ['targeted regression tests', 'contract/spec check']
    if any(x in p for x in ('random', 'simulation', 'physics', 'agent')):
        out += ['deterministic seam or fixed seed', 'bounded runtime']
    if Path(p).suffix in {'.json', '.yaml', '.yml', '.toml', '.csv'}:
        out += ['schema/parser validation', 'representative data check']
    if Path(p).suffix in {'.py', '.cs', '.go', '.c', '.h', '.cpp', '.hpp', '.gd'}:
        out += ['targeted tests', 'syntax/build check']
    return list(dict.fromkeys(out)) or ['targeted validation']


def main():
    ap = argparse.ArgumentParser(description='Suggest smallest sufficient validation for changed files.')
    ap.add_argument('files', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    rows = [{'file': f, 'evidence': classify(f)} for f in args.files]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            print(row['file'])
            for ev in row['evidence']:
                print(f'  - {ev}')

if __name__ == '__main__':
    main()
