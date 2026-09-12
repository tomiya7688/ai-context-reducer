#!/usr/bin/env python3
import argparse, re
from pathlib import Path

CHECKS={
    'goal': ('goal','目的'),
    'required': ('required','requirement','要件','必須','制約'),
    'acceptance': ('acceptance','完了条件','受け入れ','completion'),
    'deferred': ('deferred','out of scope','非対象','対象外'),
    'source': ('source','target file','対象ファイル','実装'),
    'tests': ('test','tests','検証','validation'),
}

def main():
    ap=argparse.ArgumentParser(description='Check whether task context is sufficient to stop broad exploration.')
    ap.add_argument('file')
    args=ap.parse_args(); text=Path(args.file).read_text(encoding='utf-8', errors='ignore').lower()
    results={k:any(w in text for w in words) for k,words in CHECKS.items()}
    required=('goal','required','acceptance','source','tests')
    ready=all(results[k] for k in required)
    for k,v in results.items(): print(f'{k}={"yes" if v else "no"}')
    print('stop_broad_exploration=' + ('yes' if ready else 'no'))
    if not ready:
        missing=[k for k in required if not results[k]]
        print('missing=' + ', '.join(missing))

if __name__=='__main__': main()
