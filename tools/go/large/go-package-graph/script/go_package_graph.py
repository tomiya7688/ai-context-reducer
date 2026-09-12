#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path

def module_path(root):
    gomod=root/'go.mod'
    if not gomod.exists(): return ''
    m=re.search(r'^module\s+(.+)$',gomod.read_text(encoding='utf-8',errors='ignore'),re.M)
    return m.group(1).strip() if m else ''

def imports(text):
    out=set(re.findall(r'import\s+(?:\w+\s+)?"([^"]+)"',text))
    for block in re.findall(r'import\s*\((.*?)\)',text,re.S): out.update(re.findall(r'"([^"]+)"',block))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--limit',type=int,default=1500); a=ap.parse_args(); root=Path(a.root).resolve(); mod=module_path(root); packages={}; count=0
    for p in sorted(root.rglob('*.go')):
        if 'vendor' in p.parts: continue
        rel=p.parent.relative_to(root).as_posix(); pkg=mod + (('/'+rel) if rel!='.' and mod else rel if rel!='.' else '')
        packages.setdefault(pkg,set()).update(imports(p.read_text(encoding='utf-8',errors='ignore'))); count+=1
        if count>=a.limit: break
    local=set(packages); edges=[]
    for src,deps in packages.items():
        for d in sorted(deps):
            if d in local: edges.append({'from':src,'to':d})
    print(json.dumps({'root':root.name,'module':mod,'packages':len(packages),'edges':edges,'truncated':count>=a.limit},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
