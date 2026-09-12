#!/usr/bin/env python3
import argparse
from pathlib import Path

SKIP = {'.git','node_modules','build','dist','bin','obj','.venv','venv','__pycache__','.godot'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--limit', type=int, default=30)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    rows = []
    for p in root.rglob('*'):
        if not p.is_file() or any(part in SKIP for part in p.parts):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        rows.append((size, len(p.relative_to(root).parts), str(p.relative_to(root))))
    for size, depth, name in sorted(rows, reverse=True)[:args.limit]:
        print(f'{size:>10} bytes depth={depth} {name}')

if __name__ == '__main__':
    main()
