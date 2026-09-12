#!/usr/bin/env python3
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

SKIP = {'.git', '.venv', 'venv', 'node_modules', '__pycache__'}


def role(p):
    low = '/'.join(x.lower() for x in p.parts)
    if any(x in low for x in ('/build/', '/dist/', '/bin/', '/obj/', '/cache/', '/generated/')):
        return 'generated'
    if p.suffix.lower() in {'.md', '.rst', '.txt'} or 'docs/' in low or 'doc/' in low:
        return 'docs'
    if 'test' in p.name.lower() or '/tests/' in low or '/test/' in low:
        return 'tests'
    if p.suffix.lower() in {'.py','.cs','.go','.c','.h','.cpp','.cc','.cxx','.hpp','.hh','.gd','.rs','.java','.js','.ts'}:
        return 'source'
    if p.suffix.lower() in {'.json','.yaml','.yml','.toml','.ini','.cfg','.xml'}:
        return 'config'
    if p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif','.wav','.mp3','.ogg','.mp4','.zip','.7z'}:
        return 'asset/binary'
    return 'other'


def main():
    ap = argparse.ArgumentParser(description='Classify repository files by likely context role.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    groups = defaultdict(list)
    for p in root.rglob('*'):
        if not p.is_file() or any(part in SKIP for part in p.parts):
            continue
        groups[role(p.relative_to(root))].append(str(p.relative_to(root)))
    data = {k: {'count': len(v), 'examples': v[:12]} for k,v in sorted(groups.items())}
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for k,v in data.items():
            print(f'{k}: {v["count"]}')
            for x in v['examples']:
                print(f'  - {x}')

if __name__ == '__main__':
    main()
