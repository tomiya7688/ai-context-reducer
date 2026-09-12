#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

IGNORE = {'.git', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist', '__pycache__'}


def main():
    ap = argparse.ArgumentParser(description='Build a compact heading index for docs.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--max-files', type=int, default=200)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    rows = []
    for p in root.rglob('*.md'):
        if any(part in IGNORE for part in p.parts):
            continue
        try:
            text = p.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        heads = []
        for n, line in enumerate(text.splitlines(), 1):
            m = re.match(r'^(#{1,3})\s+(.+?)\s*$', line)
            if m:
                heads.append({'line': n, 'level': len(m.group(1)), 'title': m.group(2)[:120]})
        if heads:
            rows.append({'file': str(p.relative_to(root)), 'headings': heads[:60]})
        if len(rows) >= args.max_files:
            break
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            print(row['file'])
            for h in row['headings']:
                print(f"  L{h['line']} {'#' * h['level']} {h['title']}")

if __name__ == '__main__':
    main()
