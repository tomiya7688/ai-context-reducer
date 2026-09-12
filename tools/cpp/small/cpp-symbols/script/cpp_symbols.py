#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
PAT=[('namespace',re.compile(r'^\s*namespace\s+([A-Za-z_]\w*)')),('class',re.compile(r'^\s*(?:class|struct)\s+([A-Za-z_]\w*)')),('func',re.compile(r'^\s*(?:template\s*<[^>]+>\s*)?(?:[\w:<>,~*&\[\]\s]+)\s+([A-Za-z_~]\w*)\s*\([^;]*\)\s*(?:const\s*)?(?:\{|$)'))]
def scan(p):
    rows=[]
    for i,line in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
        for kind,pat in PAT:
            m=pat.search(line)
            if m: rows.append({'kind':kind,'name':m.group(1),'line':i}); break
    return {'file':str(p),'symbols':rows}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('paths',nargs='+'); a=ap.parse_args(); out=[]
    exts={'.cpp','.cc','.cxx','.hpp','.hh','.hxx','.h'}
    for raw in a.paths:
        p=Path(raw)
        if p.is_dir(): out.extend(scan(f) for f in sorted(p.rglob('*')) if f.suffix.lower() in exts)
        elif p.suffix.lower() in exts: out.append(scan(p))
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
