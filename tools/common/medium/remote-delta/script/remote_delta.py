#!/usr/bin/env python3
import argparse
from pathlib import Path

from commander import build_remote_delta


def main():
    parser = argparse.ArgumentParser(description='Show compact local/remote git delta without dumping a full diff.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--base', default='HEAD')
    parser.add_argument('--remote', default='origin/HEAD')
    parser.add_argument('--max-files', type=int, default=40)
    args = parser.parse_args()

    print(
        build_remote_delta(
            Path(args.root).resolve(),
            base=args.base,
            remote=args.remote,
            max_files=args.max_files,
        ),
        end='',
    )


if __name__ == '__main__':
    main()
