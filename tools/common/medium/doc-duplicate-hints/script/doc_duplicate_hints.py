#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from messenger import iter_documents, read_lines
from processing import collect_duplicates


# emit は内部結果を安定した利用者向け表現へ変換する。
def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main() -> int:
    parser = argparse.ArgumentParser(description='Find repeated documentation lines as compact self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--min-chars', type=int, default=50)
    parser.add_argument('--max-groups', type=int, default=80, help='Maximum duplicate groups returned. 0 means unlimited.')
    parser.add_argument('--max-occurrences-per-group', type=int, default=10, help='Maximum occurrences returned per group. 0 means unlimited.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        emit({'tool': 'doc-duplicate-hints', 'status': 'input_missing', 'root_path': str(root)})
        return 2
    if not root.is_dir():
        emit({'tool': 'doc-duplicate-hints', 'status': 'input_not_directory', 'root_path': str(root)})
        return 2

    documents = []
    read_errors = []
    scan_stats = {'walk_error_count': 0}
    discovered_documents = 0
    for path in iter_documents(root, scan_stats):
        discovered_documents += 1
        lines = read_lines(path)
        if lines is None:
            read_errors.append(path.relative_to(root).as_posix())
            continue
        documents.append((path.relative_to(root).as_posix(), lines))

    all_groups = collect_duplicates(documents, args.min_chars)
    group_limit = max(0, args.max_groups)
    occurrence_limit = max(0, args.max_occurrences_per_group)
    selected_groups = all_groups if group_limit == 0 else all_groups[:group_limit]
    groups = []
    for group in selected_groups:
        occurrences = list(group['occurrences'])
        returned_occurrences = occurrences if occurrence_limit == 0 else occurrences[:occurrence_limit]
        groups.append({
            'repeated_text': group['repeated_text'],
            'occurrence_count_total': len(occurrences),
            'occurrences': returned_occurrences,
            'occurrences_truncated': len(returned_occurrences) < len(occurrences),
        })

    warnings = bool(read_errors or scan_stats['walk_error_count'])
    result = {
        'tool': 'doc-duplicate-hints',
        'status': 'partial' if warnings else 'ok',
        'root_path': str(root),
        'discovered_documents': discovered_documents,
        'scanned_documents': len(documents),
        'duplicate_group_count_total': len(all_groups),
        'duplicate_groups': groups,
        'duplicate_groups_truncated': len(groups) < len(all_groups),
        'read_error_paths': read_errors,
        'walk_error_count': scan_stats['walk_error_count'],
    }
    emit(result)
    return 0


if __name__ == '__main__':
    sys.exit(main())
