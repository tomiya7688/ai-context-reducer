#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
REF=re.compile(r'<ProjectReference\s+Include="([^"]+)"')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); root=Path(a.root).resolve(); projects={}
    for p in sorted(root.rglob('*.csproj')):
        if any(x in p.parts for x in ('bin','obj')): continue
        rel=p.relative_to(root).as_posix(); refs=[]
        for raw in REF.findall(p.read_text(encoding='utf-8',errors='ignore')):
            target=(p.parent/Path(raw.replace('\\','/'))).resolve()
            try: refs.append(target.relative_to(root).as_posix())
            except ValueError: refs.append(raw)
        projects[rel]=sorted(set(refs))
    edges=[{'from':src,'to':dst} for src,refs in projects.items() for dst in refs]
    print(json.dumps({'root':root.name,'projects':sorted(projects),'edges':edges},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
