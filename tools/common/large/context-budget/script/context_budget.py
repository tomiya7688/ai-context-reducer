#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from messenger import iter_text_files
from processing import estimate_accurate, estimate_fast, summarize


# emit は候補fileのtoken estimate・priority・budget超過を利用者向けに出力します。
def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


# main は候補fileのtoken estimateとpriorityを集計し、budget内の読込案を出力します。
def main():
    parser = argparse.ArgumentParser(description='Estimate how much agent context candidate text would consume.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--top', type=int, default=40)
    parser.add_argument('--mode', choices=['fast', 'accurate'], default='fast')
    parser.add_argument('--max-files', type=int, default=0, help='Optional safety limit. 0 means no file-count limit.')
    parser.add_argument('--include-ignored', action='store_true')
    args = parser.parse_args()
    if args.top < 0 or args.max_files < 0:
        parser.error('--top and --max-files must be non-negative')

    root = Path(args.root).resolve()
    if not root.exists():
        emit({'tool': 'context-budget', 'status': 'input_missing', 'root_path': str(root)})
        return 2
    if not root.is_dir():
        emit({'tool': 'context-budget', 'status': 'input_not_directory', 'root_path': str(root)})
        return 2

    estimator = estimate_accurate if args.mode == 'accurate' else estimate_fast
    rows = []
    scanned = 0
    estimation_errors = 0
    truncated = False
    scan_stats = {'walk_error_count': 0}

    for path in iter_text_files(root, args.include_ignored, scan_stats):
        if args.max_files > 0 and scanned >= args.max_files:
            truncated = True
            break
        result = estimator(path)
        if result is None:
            estimation_errors += 1
            continue
        tokens, size = result
        rows.append((tokens, size, path.relative_to(root).as_posix()))
        scanned += 1

    result = summarize(
        rows,
        max(0, args.top),
        args.mode,
        scanned,
        truncated,
        estimation_errors,
        scan_stats['walk_error_count'],
    )
    result['root_path'] = str(root)
    emit(result)
    return 0 if result['status'] in {'ok', 'ok_with_warnings'} else 2


if __name__ == '__main__':
    raise SystemExit(main())
