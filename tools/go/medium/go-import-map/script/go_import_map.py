#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
BLOCK=re.compile(r'import\s*\((.*?)\)',re.S); SINGLE=re.compile(r'import\s+(?:\w+\s+)?"([^"]+)"')
def imports(p):
    text=p.read_text(encoding='utf-8',errors='ignore'); out=set(SINGLE.findall(text))
    for block in BLOCK.findall(text): out.update(re.findall(r'"([^"]+)"',block))
    return sorted(out)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--limit',type=int,default=500); a=ap.parse_args(); root=Path(a.root).resolve(); rows=[]
    for p in sorted(root.rglob('*.go')):
        if 'vendor' in p.parts: continue
        rows.append({'file':p.relative_to(root).as_posix(),'imports':imports(p)})
        if len(rows)>=a.limit: break
    print(json.dumps({'root':root.name,'files':rows,'truncated':len(rows)>=a.limit},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
