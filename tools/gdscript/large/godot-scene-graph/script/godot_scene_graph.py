#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
EXT=re.compile(r'^\[ext_resource\s+type="([^"]+)"\s+path="([^"]+)"',re.M)
NODE=re.compile(r'^\[node\s+name="([^"]+)"(?:\s+type="([^"]+)")?',re.M)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--limit',type=int,default=1200); a=ap.parse_args(); root=Path(a.root).resolve(); scenes=[]; count=0
    for p in sorted(root.rglob('*.tscn')):
        text=p.read_text(encoding='utf-8',errors='ignore')
        scenes.append({'scene':p.relative_to(root).as_posix(),'external_resources':[{'type':t,'path':path} for t,path in EXT.findall(text)],'nodes':[{'name':n,'type':typ or None} for n,typ in NODE.findall(text)][:200]})
        count+=1
        if count>=a.limit: break
    print(json.dumps({'root':root.name,'scenes':scenes,'truncated':count>=a.limit},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
