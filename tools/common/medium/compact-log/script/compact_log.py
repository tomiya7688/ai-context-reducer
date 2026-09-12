#!/usr/bin/env python3
import argparse, re, sys
from pathlib import Path

PAT=re.compile(r'(error|failed|failure|fatal|exception|warning|warn|assert|traceback|ng\b)', re.I)

def main():
    ap=argparse.ArgumentParser(description='Reduce long validation logs to high-signal lines plus a bounded tail.')
    ap.add_argument('file', nargs='?')
    ap.add_argument('--max-findings', type=int, default=80)
    ap.add_argument('--tail', type=int, default=20)
    args=ap.parse_args()
    text=Path(args.file).read_text(encoding='utf-8', errors='ignore') if args.file else sys.stdin.read()
    lines=text.splitlines(); findings=[]
    for n,line in enumerate(lines,1):
        if PAT.search(line): findings.append((n,line))
    print(f'lines={len(lines)} findings={len(findings)}')
    if findings:
        print('findings:')
        for n,line in findings[:args.max_findings]: print(f'  {n}: {line[:240]}')
        if len(findings)>args.max_findings: print(f'  ... truncated {len(findings)-args.max_findings} more findings')
    print('tail:')
    start=max(0,len(lines)-args.tail)
    for i,line in enumerate(lines[start:],start+1): print(f'  {i}: {line[:240]}')

if __name__=='__main__': main()
