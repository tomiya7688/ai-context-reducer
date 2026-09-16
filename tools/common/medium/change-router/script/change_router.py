#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from commander import route_changes


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Route changed files to likely tests and docs as self-describing JSON.'
    )
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--base')
    parser.add_argument('--changed', action='append', default=[])
    parser.add_argument('--max-changed', type=int, default=80,
                        help='Maximum changed files returned/routed. 0 means unlimited.')
    parser.add_argument('--max-index-files', type=int, default=0,
                        help='Optional safety limit for indexed test/doc candidates. 0 means unlimited.')
    parser.add_argument('--per-kind', type=int, default=8,
                        help='Maximum test/doc candidates returned per changed file. 0 means unlimited.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        emit({'tool': 'change-router', 'status': 'input_missing', 'root_path': str(root)})
        return 2
    if not root.is_dir():
        emit({'tool': 'change-router', 'status': 'input_not_directory', 'root_path': str(root)})
        return 2

    result = route_changes(
        root=root,
        base=args.base,
        explicit_changed=args.changed,
        max_changed=args.max_changed,
        max_index_files=args.max_index_files,
        candidate_limit=args.per_kind,
    )
    result['root_path'] = str(root)
    emit(result)
    return 0 if result['status'] not in {'git_diff_unavailable'} else 2


if __name__ == '__main__':
    sys.exit(main())
