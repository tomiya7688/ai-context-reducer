#!/usr/bin/env python3
import argparse
from pathlib import Path

NAMES={
    'architecture': ('architecture','design','設計'),
    'specification': ('spec','specification','仕様'),
    'coding-rules': ('coding','rules','style','規約'),
    'ai-context': ('ai_context','agents','claude'),
    'current-state': ('state','status','current'),
    'tasks': ('roadmap','backlog','todo','issue','予定'),
}

def main():
    ap=argparse.ArgumentParser(description='Find likely source-of-truth documents by filename only; never treats guesses as authoritative.')
    ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args(); root=Path(args.root).resolve(); hits={k:[] for k in NAMES}
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.md','.txt','.rst'}: continue
        name=p.name.lower()
        for role, words in NAMES.items():
            if any(w in name for w in words): hits[role].append(p.relative_to(root).as_posix())
    for role, paths in hits.items():
        print(role + ':')
        if paths:
            for x in sorted(paths)[:20]: print('  - ' + x)
        else: print('  - not found')
    print('\nNote: candidates only. Confirm authority from project instructions/source before using as Source of Truth.')

if __name__=='__main__': main()
