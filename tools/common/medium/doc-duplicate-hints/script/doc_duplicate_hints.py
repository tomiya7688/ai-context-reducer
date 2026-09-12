#!/usr/bin/env python3
import argparse, hashlib, re
from collections import defaultdict
from pathlib import Path


def normalize(line):
    line=re.sub(r'\s+',' ',line.strip().lower())
    line=re.sub(r'[`*_>#-]','',line).strip()
    return line

def main():
    ap=argparse.ArgumentParser(description='Find repeated non-trivial documentation lines that may indicate duplicated context.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--min-chars', type=int, default=50)
    ap.add_argument('--max', type=int, default=80)
    args=ap.parse_args(); root=Path(args.root).resolve(); seen=defaultdict(list)
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.md','.txt','.rst'}: continue
        try: lines=p.read_text(encoding='utf-8', errors='ignore').splitlines()
        except Exception: continue
        for n,line in enumerate(lines,1):
            norm=normalize(line)
            if len(norm)<args.min_chars: continue
            key=hashlib.sha1(norm.encode()).hexdigest()
            seen[key].append((p.relative_to(root).as_posix(),n,line.strip()))
    count=0
    for items in seen.values():
        files={x[0] for x in items}
        if len(files)<2: continue
        print('duplicate: ' + items[0][2][:180])
        for f,n,_ in items[:10]: print(f'  - {f}:{n}')
        count+=1
        if count>=args.max:
            print(f'... truncated at {args.max} groups')
            break
    if count==0: print('no repeated long lines found')

if __name__=='__main__': main()
