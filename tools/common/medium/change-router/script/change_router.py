#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from commander import route_changes


def main():
    parser = argparse.ArgumentParser(
        description='Route changed files to likely tests and docs using one bounded repository index.'
    )
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--base')
    parser.add_argument('--changed', action='append', default=[])
    parser.add_argument('--max-changed', type=int, default=80)
    parser.add_argument('--max-index-files', type=int, default=12000)
    parser.add_argument('--per-kind', type=int, default=8)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    result = route_changes(
        root=Path(args.root).resolve(),
        base=args.base,
        explicit_changed=args.changed,
        max_changed=args.max_changed,
        max_index_files=args.max_index_files,
        candidate_limit=args.per_kind,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    truncated = result['truncated']
    if truncated['index']:
        print(
            f"[index truncated at {result['index_candidates']} candidates; "
            'raise --max-index-files only when broader routing is required]'
        )
    if truncated['changed']:
        print(
            f"[changed files truncated at {args.max_changed}; "
            'narrow the diff or raise --max-changed intentionally]'
        )

    for row in result['routes']:
        print(row['changed'])
        if row['tests']:
            print('  tests: ' + ', '.join(row['tests']))
        if row['docs']:
            print('  docs: ' + ', '.join(row['docs']))


if __name__ == '__main__':
    main()
