#!/usr/bin/env python3
import argparse

from messenger import iter_policy_files, read_lines
from processing import policy_findings


def main():
    parser = argparse.ArgumentParser(description='Index likely policy/rule lines without loading whole policy documents into agent context.')
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--max', type=int, default=120)
    args = parser.parse_args()

    count = 0
    for path in iter_policy_files(args.paths):
        lines = read_lines(path)
        if lines is None:
            continue
        for number, heading, text in policy_findings(lines):
            print(f'{path}:{number} [{heading}] {text}')
            count += 1
            if count >= args.max:
                print(f'... truncated at {args.max} findings')
                return


if __name__ == '__main__':
    main()
