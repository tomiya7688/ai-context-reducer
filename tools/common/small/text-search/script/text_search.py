#!/usr/bin/env python3
"""Small dependency-free text search for ai-context-reducer.

Not a ripgrep replacement in speed/features. It is a portable fallback for
Search-first / Read-second when rg is unavailable.
"""
import argparse
import fnmatch
import re
from pathlib import Path

DEFAULT_IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs'
}


def iter_files(root: Path, globs, excludes, max_bytes):
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in DEFAULT_IGNORE for part in rel.parts):
            continue
        text = rel.as_posix()
        if any(fnmatch.fnmatch(text, pat) for pat in excludes):
            continue
        if globs and not any(fnmatch.fnmatch(text, pat) for pat in globs):
            continue
        try:
            if p.stat().st_size > max_bytes:
                continue
        except OSError:
            continue
        yield p


def looks_binary(path: Path):
    try:
        data = path.read_bytes()[:4096]
    except OSError:
        return True
    return b'\x00' in data


def main():
    ap = argparse.ArgumentParser(description='Portable bounded text search fallback.')
    ap.add_argument('pattern')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('-i', '--ignore-case', action='store_true')
    ap.add_argument('-F', '--fixed-string', action='store_true')
    ap.add_argument('-g', '--glob', action='append', default=[])
    ap.add_argument('--exclude', action='append', default=[])
    ap.add_argument('--max-results', type=int, default=100)
    ap.add_argument('--max-file-bytes', type=int, default=2_000_000)
    ap.add_argument('--context', type=int, default=0)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    flags = re.IGNORECASE if args.ignore_case else 0
    expr = re.escape(args.pattern) if args.fixed_string else args.pattern
    try:
        regex = re.compile(expr, flags)
    except re.error as exc:
        raise SystemExit(f'invalid regex: {exc}')

    count = 0
    for path in iter_files(root, args.glob, args.exclude, args.max_file_bytes):
        if looks_binary(path):
            continue
        try:
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            if not regex.search(line):
                continue
            start = max(0, i - args.context)
            end = min(len(lines), i + args.context + 1)
            rel = path.relative_to(root).as_posix()
            for j in range(start, end):
                marker = ':' if j == i else '-'
                print(f'{rel}{marker}{j + 1}{marker}{lines[j]}')
            count += 1
            if count >= args.max_results:
                print(f'-- truncated after {count} matches --')
                return


if __name__ == '__main__':
    main()
