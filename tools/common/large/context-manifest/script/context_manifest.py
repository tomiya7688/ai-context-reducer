#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from messenger import collect_files
from processing import build_manifest


def main():
    parser = argparse.ArgumentParser(description='Build a prioritized context manifest.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=400)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result = build_manifest(collect_files(root), args.limit)
    result['root'] = root.name
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
