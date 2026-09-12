#!/usr/bin/env python3
import argparse
from pathlib import Path

IGNORE={'.git','.venv','venv','node_modules','bin','obj','build','dist','__pycache__','.godot'}
TEXT={'.py','.cs','.go','.c','.h','.cpp','.cc','.cxx','.hpp','.hh','.gd','.md','.txt','.rst','.json','.yaml','.yml','.toml','.xml','.ini'}

def main():
    ap=argparse.ArgumentParser(description='Estimate reading cost of candidate text files before adding them to AI context.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--top', type=int, default=40)
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=[]
    for p in root.rglob('*'):
        if any(part.lower() in IGNORE for part in p.parts) or not p.is_file() or p.suffix.lower() not in TEXT: continue
        try:
            text=p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        chars=len(text); lines=text.count('\n')+1; est_tokens=max(1, chars//4)
        rows.append((est_tokens,lines,p.relative_to(root).as_posix()))
    rows.sort(reverse=True)
    total=sum(x[0] for x in rows)
    print(f'estimated_total_tokens_if_all_text_read={total}')
    print('largest_candidates:')
    for tok,lines,path in rows[:args.top]:
        print(f'  {tok:>8} tok  {lines:>6} lines  {path}')
    if len(rows)>args.top: print(f'  ... {len(rows)-args.top} more files')

if __name__=='__main__': main()
