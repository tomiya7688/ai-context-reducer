#!/usr/bin/env python3
import argparse
from pathlib import Path

from commander import build_context_pack


def main():
    parser = argparse.ArgumentParser(description='Generate a small task Context Pack skeleton from git state.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--goal', default='')
    parser.add_argument('--required', default='')
    parser.add_argument('--acceptance', default='')
    parser.add_argument('--deferred', default='')
    parser.add_argument('--max-state-lines', type=int, default=60)
    parser.add_argument('--output')
    args = parser.parse_args()

    task = {
        'goal': args.goal,
        'required': args.required,
        'acceptance': args.acceptance,
        'deferred': args.deferred,
    }
    text = build_context_pack(Path(args.root).resolve(), task, args.max_state_lines)

    if args.output:
        Path(args.output).write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
