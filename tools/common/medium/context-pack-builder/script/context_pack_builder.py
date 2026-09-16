#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from commander import build_context_pack


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a small task Context Pack skeleton from git state.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--goal', default='')
    parser.add_argument('--required', default='')
    parser.add_argument('--acceptance', default='')
    parser.add_argument('--deferred', default='')
    parser.add_argument('--max-state-lines', type=int, default=60)
    parser.add_argument('--output')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f'context-pack-builder: input_missing: {root}', file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f'context-pack-builder: input_not_directory: {root}', file=sys.stderr)
        return 2

    task = {
        'goal': args.goal,
        'required': args.required,
        'acceptance': args.acceptance,
        'deferred': args.deferred,
    }
    text = build_context_pack(root, task, max(0, args.max_state_lines))

    if args.output:
        try:
            Path(args.output).write_text(text, encoding='utf-8')
        except OSError as exc:
            print(f'context-pack-builder: output_write_failed: {exc}', file=sys.stderr)
            return 2
    else:
        print(text, end='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
