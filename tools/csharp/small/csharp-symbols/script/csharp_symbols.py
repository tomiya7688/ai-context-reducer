#!/usr/bin/env python3
import argparse,re,json
from pathlib import Path

PATTERNS=[('namespace',re.compile(r'^\s*namespace\s+([A-Za-z_][\w\.]*)')),('class',re.compile(r'^\s*(?:public|private|internal|protected|static|sealed|abstract|partial|\s)*\s*class\s+([A-Za-z_]\w*)')),('interface',re.compile(r'^\s*(?:public|private|internal|protected|partial|\s)*\s*interface\s+([A-Za-z_]\w*)')),('method',re.compile(r'^\s*(?:public|private|internal|protected|static|virtual|override|async|sealed|partial|extern|new|\s)+[\w<>,\[\]\.?]+\s+([A-Za-z_]\w*)\s*\('))]

def scan(p):
    out=[]
    try: lines=p.read_text(encoding='utf-8',errors='ignore').splitlines()
    except Exception as e: return {'file':str(p),'error':str(e)}
    for i,line in enumerate(lines,1):
        for kind,pat in PATTERNS:
            m=pat.search(line)
            if m: out.append({'kind':kind,'name':m.group(1),'line':i}); break
    return {'file':str(p),'symbols':out}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('paths',nargs='+'); a=ap.parse_args(); rows=[]
    for raw in a.paths:
        p=Path(raw)
        if p.is_dir(): rows.extend(scan(f) for f in sorted(p.rglob('*.cs')) if not any(x in f.parts for x in ('bin','obj')))
        elif p.suffix.lower()=='.cs': rows.append(scan(p))
    print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
