#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
PAT=[('class_name',re.compile(r'^\s*class_name\s+([A-Za-z_]\w*)')),('class',re.compile(r'^\s*class\s+([A-Za-z_]\w*)')),('func',re.compile(r'^\s*func\s+([A-Za-z_]\w*)\s*\(')),('signal',re.compile(r'^\s*signal\s+([A-Za-z_]\w*)')),('var',re.compile(r'^\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:var|const)\s+([A-Za-z_]\w*)'))]
def scan(p):
    rows=[]
    for i,line in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
        for kind,pat in PAT:
            m=pat.search(line)
            if m: rows.append({'kind':kind,'name':m.group(1),'line':i}); break
    return {'file':str(p),'symbols':rows}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('paths',nargs='+'); a=ap.parse_args(); out=[]
    for raw in a.paths:
        p=Path(raw)
        if p.is_dir(): out.extend(scan(f) for f in sorted(p.rglob('*.gd')))
        elif p.suffix.lower()=='.gd': out.append(scan(p))
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
