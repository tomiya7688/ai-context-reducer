#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', 'bin', 'obj',
    'build', 'dist', '__pycache__', '.godot', '.idea', '.vs', 'vendor',
}
TEXT = {
    '.py', '.cs', '.go', '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh',
    '.gd', '.md', '.txt', '.rst', '.json', '.yaml', '.yml', '.toml', '.xml', '.ini',
}


def iter_text_files(root: Path, include_ignored: bool):
    for current, dirs, files in os.walk(root):
        if not include_ignored:
            dirs[:] = [d for d in dirs if d.lower() not in IGNORE]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            if path.suffix.lower() in TEXT:
                yield path


def estimate_fast(path: Path):
    try:
        size = path.stat().st_size
    except OSError:
        return None
    return max(1, size // 4), size


def estimate_accurate(path: Path):
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return None
    size = len(text.encode('utf-8', errors='ignore'))
    return max(1, len(text) // 4), size


def main():
    parser = argparse.ArgumentParser(
        description='Estimate how much agent context candidate text would consume.'
    )
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--top', type=int, default=40)
    parser.add_argument('--mode', choices=['fast', 'accurate'], default='fast')
    parser.add_argument('--max-files', type=int, default=0,
                        help='Optional safety limit. 0 means no file-count limit.')
    parser.add_argument('--include-ignored', action='store_true',
                        help='Include dependency/generated/cache directories when they are intentionally part of the analysis scope.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    estimator = estimate_accurate if args.mode == 'accurate' else estimate_fast
    rows = []
    scanned = 0
    truncated = False

    for path in iter_text_files(root, args.include_ignored):
        result = estimator(path)
        if result is None:
            continue
        tokens, size = result
        rows.append((tokens, size, path.relative_to(root).as_posix()))
        scanned += 1
        if args.max_files > 0 and scanned >= args.max_files:
            truncated = True
            break

    rows.sort(reverse=True)
    total = sum(row[0] for row in rows)

    print(f'mode={args.mode}')
    print(f'estimated_total_tokens_if_all_candidates_read={total}')
    print(f'scanned_text_files={scanned}')
    print(f'truncated={str(truncated).lower()}')
    print('largest_candidates:')
    for tokens, size, path in rows[:args.top]:
        suffix = '' if args.mode == 'accurate' else '~'
        print(f'  {tokens:>8} tok{suffix}  {size:>10} bytes  {path}')
    if len(rows) > args.top:
        print(f'  ... {len(rows) - args.top} more analyzed files')


if __name__ == '__main__':
    main()
