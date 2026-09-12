#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
LOAD=re.compile(r'(?:load|preload)\(\s*["\']([^"\']+)["\']\s*\)')
EXTENDS=re.compile(r'^\s*extends\s+["\']([^"\']+)["\']',re.M)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--limit',type=int,default=800); a=ap.parse_args(); root=Path(a.root).resolve(); rows=[]
    for p in sorted(root.rglob('*.gd')):
        text=p.read_text(encoding='utf-8',errors='ignore'); deps=set(LOAD.findall(text)); deps.update(EXTENDS.findall(text)); rows.append({'file':p.relative_to(root).as_posix(),'dependencies':sorted(deps)})
        if len(rows)>=a.limit: break
    print(json.dumps({'root':root.name,'files':rows,'truncated':len(rows)>=a.limit},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
