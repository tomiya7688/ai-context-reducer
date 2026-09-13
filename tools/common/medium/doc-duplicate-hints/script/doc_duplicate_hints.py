#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from messenger import iter_documents, read_lines
from processing import collect_duplicates


def main():
    parser = argparse.ArgumentParser(description='Find repeated documentation lines as compact self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--min-chars', type=int, default=50)
    parser.add_argument('--max-groups', type=int, default=80)
    parser.add_argument('--max-occurrences-per-group', type=int, default=10)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    documents = []
    read_errors = []
    for path in iter_documents(root):
        lines = read_lines(path)
        if lines is None:
            read_errors.append(path.relative_to(root).as_posix())
            continue
        documents.append((path.relative_to(root).as_posix(), lines))

    all_groups = collect_duplicates(documents, args.min_chars)
    groups = []
    for group in all_groups[:args.max_groups]:
        occurrences = list(group['occurrences'])
        groups.append({
            'repeated_text': group['repeated_text'],
            'occurrences': occurrences[:args.max_occurrences_per_group],
            'occurrences_truncated': len(occurrences) > args.max_occurrences_per_group,
        })

    result = {
        'tool': 'doc-duplicate-hints',
        'status': 'partial' if read_errors else 'ok',
        'scanned_documents': len(documents),
        'duplicate_groups': groups,
        'duplicate_groups_truncated': len(all_groups) > args.max_groups,
        'read_error_paths': read_errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
