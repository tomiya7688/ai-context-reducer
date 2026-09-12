#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
INC=re.compile(r'^\s*#\s*include\s*"([^"]+)"',re.M)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--limit',type=int,default=1500); a=ap.parse_args(); root=Path(a.root).resolve(); files=[]
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.suffix.lower() in {'.c','.h'}: files.append(p)
        if len(files)>=a.limit: break
    relmap={p.relative_to(root).as_posix():p for p in files}; byname={p.name:rel for rel,p in relmap.items()}; edges=[]
    for rel,p in relmap.items():
        for inc in INC.findall(p.read_text(encoding='utf-8',errors='ignore')):
            target=inc if inc in relmap else byname.get(Path(inc).name)
            if target: edges.append({'from':rel,'to':target})
    print(json.dumps({'root':root.name,'files':len(files),'edges':edges,'truncated':len(files)>=a.limit},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
