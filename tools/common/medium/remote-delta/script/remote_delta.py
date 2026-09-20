#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from commander import build_remote_delta


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    parser = argparse.ArgumentParser(description='Show compact local/remote git delta as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--base', default='HEAD')
    parser.add_argument('--remote', default='origin/HEAD')
    parser.add_argument('--max-files', type=int, default=40)
    args = parser.parse_args()

    result = build_remote_delta(
        Path(args.root).resolve(),
        base=args.base,
        remote=args.remote,
        max_files=args.max_files,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
