#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


# 指定fileの必要範囲だけをboundedに切り出し、全file読込を避けるCLI境界を提供する。
def main():
    parser = argparse.ArgumentParser(description='Return bounded excerpts around matching lines as self-describing JSON.')
    parser.add_argument('pattern')
    parser.add_argument('files', nargs='+')
    parser.add_argument('--before', type=int, default=3)
    parser.add_argument('--after', type=int, default=5)
    parser.add_argument('--max-matches', type=int, default=20)
    args = parser.parse_args()

    try:
        regex = re.compile(args.pattern, re.IGNORECASE)
    except re.error:
        print(json.dumps({
            'tool': 'target-slice',
            'status': 'invalid_pattern',
            'pattern': args.pattern,
        }, ensure_ascii=False, indent=2))
        return

    matches = []
    unreadable_files = []
    missing_files = []
    truncated = False

    for name in args.files:
        path = Path(name)
        if not path.exists():
            missing_files.append(str(path))
            continue
        try:
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            unreadable_files.append(str(path))
            continue

        for index, line in enumerate(lines):
            if not regex.search(line):
                continue
            start = max(0, index - args.before)
            end = min(len(lines), index + args.after + 1)
            matches.append({
                'path': str(path),
                'match_line': index + 1,
                'excerpt_start_line': start + 1,
                'excerpt': [
                    {'line': number, 'text': lines[number - 1]}
                    for number in range(start + 1, end + 1)
                ],
            })
            if len(matches) >= args.max_matches:
                truncated = True
                break
        if truncated:
            break

    result = {
        'tool': 'target-slice',
        'status': 'ok',
        'pattern': args.pattern,
        'match_count': len(matches),
        'matches': matches,
        'matches_truncated': truncated,
        'missing_files': missing_files,
        'unreadable_files': unreadable_files,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
