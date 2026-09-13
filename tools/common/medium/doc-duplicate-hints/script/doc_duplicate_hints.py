#!/usr/bin/env python3
import argparse
from pathlib import Path

from messenger import iter_documents, read_lines
from processing import collect_duplicates


def main():
    parser = argparse.ArgumentParser(description='Find repeated non-trivial documentation lines that may indicate duplicated context.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--min-chars', type=int, default=50)
    parser.add_argument('--max', type=int, default=80)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    documents = []
    for path in iter_documents(root):
        lines = read_lines(path)
        if lines is not None:
            documents.append((path.relative_to(root).as_posix(), lines))

    groups = collect_duplicates(documents, args.min_chars)
    for items in groups[:args.max]:
        print('duplicate: ' + items[0][2][:180])
        for file_name, number, _ in items[:10]:
            print(f'  - {file_name}:{number}')
    if len(groups) > args.max:
        print(f'... truncated at {args.max} groups')
    elif not groups:
        print('no repeated long lines found')


if __name__ == '__main__':
    main()
