#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); root=Path(a.root).resolve(); projects=[]
    for csproj in sorted(root.rglob('*.csproj')):
        if any(x in csproj.parts for x in ('bin','obj')): continue
        text=csproj.read_text(encoding='utf-8',errors='ignore')
        refs=re.findall(r'<ProjectReference\s+Include="([^"]+)"',text)
        src=[p.relative_to(root).as_posix() for p in csproj.parent.rglob('*.cs') if not any(x in p.parts for x in ('bin','obj'))]
        projects.append({'project':csproj.relative_to(root).as_posix(),'project_references':refs,'source_files':src[:300],'source_truncated':len(src)>300})
    print(json.dumps({'root':root.name,'projects':projects},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
