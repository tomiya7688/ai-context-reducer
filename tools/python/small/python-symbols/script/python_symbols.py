#!/usr/bin/env python3
import argparse
import ast
import json
from pathlib import Path


def scan(path: Path):
    try:
        tree=ast.parse(path.read_text(encoding='utf-8'))
    except Exception as e:
        return {'file':str(path),'error':str(e)}
    symbols=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            symbols.append({'kind':type(node).__name__,'name':node.name,'line':node.lineno})
    symbols.sort(key=lambda x:x['line'])
    return {'file':str(path),'symbols':symbols}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('paths',nargs='+')
    args=ap.parse_args()
    out=[]
    for raw in args.paths:
        p=Path(raw)
        if p.is_dir():
            out.extend(scan(f) for f in sorted(p.rglob('*.py')) if '__pycache__' not in f.parts)
        elif p.suffix=='.py':
            out.append(scan(p))
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
