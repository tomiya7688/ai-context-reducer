#!/usr/bin/env python3
import argparse
import ast
import json
from pathlib import Path


def imports(path: Path):
    try:
        tree=ast.parse(path.read_text(encoding='utf-8'))
    except Exception:
        return []
    out=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            out.extend(a.name for a in node.names)
        elif isinstance(node,ast.ImportFrom):
            base='.'*node.level+(node.module or '')
            out.append(base)
    return sorted(set(out))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root',nargs='?',default='.')
    ap.add_argument('--limit',type=int,default=300)
    args=ap.parse_args()
    root=Path(args.root).resolve()
    rows=[]
    for p in sorted(root.rglob('*.py')):
        if any(x in p.parts for x in ('__pycache__','.venv','venv')):
            continue
        rows.append({'file':p.relative_to(root).as_posix(),'imports':imports(p)})
        if len(rows)>=args.limit:
            break
    print(json.dumps({'root':root.name,'files':rows,'truncated':len(rows)>=args.limit},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
