#!/usr/bin/env python3
import argparse
from pathlib import Path

NAMES = {'build','dist','bin','obj','.cache','cache','.godot','node_modules','.venv','venv','coverage','logs','log','tmp','temp','backups','backup'}
EXTS = {'.log','.tmp','.bak','.cache','.pyc','.pdb','.dll','.so','.dylib','.exe','.class','.jar','.zip','.7z'}


def main():
    ap = argparse.ArgumentParser(description='Suggest likely low-value context paths. Review before adding to ignore rules.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--limit', type=int, default=80)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    found = []
    for p in root.rglob('*'):
        rel = p.relative_to(root)
        parts = {x.lower() for x in rel.parts}
        if parts & NAMES or (p.is_file() and p.suffix.lower() in EXTS):
            found.append(str(rel))
    for item in sorted(set(found))[:args.limit]:
        print(item)
    if len(found) > args.limit:
        print('[truncated]')

if __name__ == '__main__':
    main()
