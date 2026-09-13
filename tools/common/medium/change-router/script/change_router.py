#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from commander import route_changes


def main():
    parser = argparse.ArgumentParser(
        description='Route changed files to likely tests and docs as self-describing JSON.'
    )
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--base')
    parser.add_argument('--changed', action='append', default=[])
    parser.add_argument('--max-changed', type=int, default=80,
                        help='Safety limit for changed files. 0 means unlimited.')
    parser.add_argument('--max-index-files', type=int, default=12000,
                        help='Safety limit for indexed test/doc candidates. 0 means unlimited.')
    parser.add_argument('--per-kind', type=int, default=8)
    parser.add_argument('--json', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()

    result = route_changes(
        root=Path(args.root).resolve(),
        base=args.base,
        explicit_changed=args.changed,
        max_changed=args.max_changed,
        max_index_files=args.max_index_files,
        candidate_limit=args.per_kind,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
