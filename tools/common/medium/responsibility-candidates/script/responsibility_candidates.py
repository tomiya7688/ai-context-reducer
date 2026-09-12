#!/usr/bin/env python3
import argparse
from pathlib import Path

IGNORE={'.git','.venv','venv','node_modules','bin','obj','build','dist','__pycache__','.godot'}
CODE={'.py','.cs','.go','.c','.h','.cpp','.cc','.cxx','.hpp','.hh','.gd','.rs','.java','.js','.ts'}

def main():
    ap=argparse.ArgumentParser(description='Generate a Responsibility Map starter table without inventing semantic responsibilities.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--max', type=int, default=120)
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=[]
    for p in root.rglob('*'):
        if any(part.lower() in IGNORE for part in p.parts) or not p.is_file() or p.suffix.lower() not in CODE: continue
        try: size=p.stat().st_size
        except OSError: size=0
        rows.append((size,p.relative_to(root).as_posix()))
    rows.sort(reverse=True)
    print('| Path | Size | Responsibility |')
    print('|---|---:|---|')
    for size,path in rows[:args.max]:
        print(f'| `{path}` | {size} | TODO: describe ownership in one short sentence |')
    if len(rows)>args.max: print(f'\n<!-- truncated: {len(rows)-args.max} more code files -->')

if __name__=='__main__': main()
