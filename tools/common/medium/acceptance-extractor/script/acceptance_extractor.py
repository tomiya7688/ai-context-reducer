#!/usr/bin/env python3
import argparse, re
from pathlib import Path

HEADINGS = {
    'goal': ('goal','目的','概要'),
    'required': ('required','requirements','要件','必須','制約'),
    'acceptance': ('acceptance','受け入れ','完了条件','completion','done'),
    'deferred': ('deferred','out of scope','非対象','対象外','今後','future'),
}

def section(lines, start):
    out=[]
    for i in range(start+1,len(lines)):
        if re.match(r'^#{1,6}\s+', lines[i]): break
        if lines[i].strip(): out.append(lines[i].rstrip())
    return out

def main():
    ap=argparse.ArgumentParser(description='Extract Goal/Required/Acceptance/Deferred sections from markdown task text.')
    ap.add_argument('file')
    args=ap.parse_args(); p=Path(args.file)
    lines=p.read_text(encoding='utf-8', errors='ignore').splitlines()
    found={k:[] for k in HEADINGS}
    for i,line in enumerate(lines):
        m=re.match(r'^#{1,6}\s+(.+)$', line.strip())
        if not m: continue
        title=m.group(1).lower()
        for key, words in HEADINGS.items():
            if any(w in title for w in words):
                found[key].extend(section(lines,i))
    for key in ('goal','required','acceptance','deferred'):
        print(f'## {key.capitalize()}')
        if found[key]:
            for line in found[key][:40]: print(line)
        else:
            print('- not found')
        print()

if __name__=='__main__': main()
