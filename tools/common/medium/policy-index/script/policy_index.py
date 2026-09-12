#!/usr/bin/env python3
import argparse, re
from pathlib import Path

RULE_WORDS = ('must','must not','should','should not','required','recommended','禁止','必須','推奨','してはならない','すること')

def main():
    ap=argparse.ArgumentParser(description='Index likely policy/rule lines without loading whole policy documents.')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--max', type=int, default=120)
    args=ap.parse_args(); count=0
    for raw in args.paths:
        p=Path(raw)
        files=[p] if p.is_file() else [x for x in p.rglob('*') if x.is_file() and x.suffix.lower() in {'.md','.txt','.rst'}]
        for f in files:
            try: lines=f.read_text(encoding='utf-8', errors='ignore').splitlines()
            except Exception: continue
            heading=''
            for n,line in enumerate(lines,1):
                if re.match(r'^#{1,6}\s+', line): heading=line.strip('# ').strip()
                low=line.lower()
                if any(w in low for w in RULE_WORDS):
                    print(f'{f}:{n} [{heading or "no-heading"}] {line.strip()[:220]}')
                    count+=1
                    if count>=args.max:
                        print(f'... truncated at {args.max} findings')
                        return

if __name__=='__main__': main()
