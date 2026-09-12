#!/usr/bin/env python3
import argparse
import ast
import json
from pathlib import Path

IGNORE={'.venv','venv','__pycache__','build','dist'}

def module_name(root,p):
    rel=p.relative_to(root).with_suffix('')
    parts=list(rel.parts)
    if parts and parts[-1]=='__init__': parts=parts[:-1]
    return '.'.join(parts)

def deps(p):
    try: tree=ast.parse(p.read_text(encoding='utf-8'))
    except Exception: return []
    out=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): out.update(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom) and n.module: out.add(n.module)
    return sorted(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--limit',type=int,default=1000)
    a=ap.parse_args(); root=Path(a.root).resolve(); files=[]
    for p in sorted(root.rglob('*.py')):
        if any(x in IGNORE for x in p.parts): continue
        files.append(p)
        if len(files)>=a.limit: break
    mods={module_name(root,p) for p in files}
    edges=[]
    for p in files:
        src=module_name(root,p)
        for d in deps(p):
            matches=[m for m in mods if m==d or m.startswith(d+'.') or d.startswith(m+'.')]
            if matches: edges.append({'from':src,'to':sorted(matches,key=len)[0]})
    print(json.dumps({'root':root.name,'modules':len(mods),'edges':edges,'truncated':len(files)>=a.limit},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
