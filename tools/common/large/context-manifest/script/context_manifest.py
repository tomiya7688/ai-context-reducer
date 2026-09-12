#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

IGNORE = {'.git','.venv','venv','node_modules','bin','obj','build','dist','__pycache__'}
HIGH = {'README.md','AI_CONTEXT.md','AGENTS.md','CLAUDE.md','pyproject.toml','package.json','Cargo.toml','go.mod'}


def priority(path: Path):
    name = path.name
    s = path.as_posix().lower()
    if name in HIGH:
        return 'P0'
    if '/tests/' in '/' + s or s.startswith('tests/'):
        return 'P2'
    if '/docs/' in '/' + s or s.startswith('docs/'):
        return 'P3'
    if path.suffix.lower() in {'.py','.cs','.go','.rs','.ts','.js','.cpp','.c','.h','.java'}:
        return 'P1'
    return 'P4'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--limit', type=int, default=400)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    rows=[]
    for p in root.rglob('*'):
        if not p.is_file() or any(part in IGNORE for part in p.parts):
            continue
        rel=p.relative_to(root)
        rows.append({'priority':priority(rel),'path':rel.as_posix(),'bytes':p.stat().st_size})
    order={'P0':0,'P1':1,'P2':2,'P3':3,'P4':4}
    rows.sort(key=lambda x:(order[x['priority']],x['path']))
    out={'root':root.name,'total_files':len(rows),'shown':min(len(rows),args.limit),'truncated':len(rows)>args.limit,'files':rows[:args.limit]}
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
