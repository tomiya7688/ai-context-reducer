#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
FUNC=re.compile(r'^\s*(?!if\b|for\b|while\b|switch\b)(?:[A-Za-z_]\w*[\s\*]+)+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{?\s*$')
TYPE=re.compile(r'^\s*(?:typedef\s+)?(?:struct|enum|union)\s+([A-Za-z_]\w*)')
def scan(p):
    rows=[]
    for i,line in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
        m=TYPE.search(line)
        if m: rows.append({'kind':'type','name':m.group(1),'line':i}); continue
        m=FUNC.search(line)
        if m: rows.append({'kind':'func','name':m.group(1),'line':i})
    return {'file':str(p),'symbols':rows}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('paths',nargs='+'); a=ap.parse_args(); out=[]
    for raw in a.paths:
        p=Path(raw)
        if p.is_dir(): out.extend(scan(f) for f in sorted(p.rglob('*')) if f.suffix.lower() in {'.c','.h'})
        elif p.suffix.lower() in {'.c','.h'}: out.append(scan(p))
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
