#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description='Print bounded excerpts around matching lines.')
    ap.add_argument('pattern')
    ap.add_argument('files', nargs='+')
    ap.add_argument('--before', type=int, default=3)
    ap.add_argument('--after', type=int, default=5)
    ap.add_argument('--max-matches', type=int, default=20)
    args = ap.parse_args()
    rx = re.compile(args.pattern, re.IGNORECASE)
    shown = 0
    for name in args.files:
        p = Path(name)
        try:
            lines = p.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            if not rx.search(line):
                continue
            start = max(0, i - args.before)
            end = min(len(lines), i + args.after + 1)
            print(f'--- {p}:{i+1} ---')
            for n in range(start, end):
                print(f'{n+1:>6}: {lines[n]}')
            shown += 1
            if shown >= args.max_matches:
                print('[truncated: max matches reached]')
                return

if __name__ == '__main__':
    main()
