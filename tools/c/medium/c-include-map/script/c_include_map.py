#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
INC=re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]',re.M)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--limit',type=int,default=800); a=ap.parse_args(); root=Path(a.root).resolve(); rows=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in {'.c','.h'}: continue
        rows.append({'file':p.relative_to(root).as_posix(),'includes':sorted(set(INC.findall(p.read_text(encoding='utf-8',errors='ignore'))))})
        if len(rows)>=a.limit: break
    print(json.dumps({'root':root.name,'files':rows,'truncated':len(rows)>=a.limit},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
