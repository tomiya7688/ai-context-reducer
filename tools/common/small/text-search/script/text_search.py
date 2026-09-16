#!/usr/bin/env python3
"""Portable bounded text search with optional ripgrep acceleration."""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = 'text-search'
DEFAULT_IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor', 'generated',
}
ERROR_PATH_LIMIT = 20


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def normalize_limit(value: int) -> int:
    return max(0, value)


def validate_regex(pattern: str) -> str | None:
    try:
        re.compile(pattern)
    except re.error as exc:
        return str(exc)
    return None


def relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def iter_files(root: Path, globs: list[str], excludes: list[str], max_bytes: int, stats: dict[str, object]):
    def walk_error(error: OSError) -> None:
        stats['walk_error_count'] = int(stats['walk_error_count']) + 1
        paths = stats['walk_error_paths']
        if isinstance(paths, list) and len(paths) < ERROR_PATH_LIMIT:
            paths.append(str(getattr(error, 'filename', '') or 'unknown'))

    for current, dirs, files in os.walk(root, onerror=walk_error):
        dirs[:] = sorted(d for d in dirs if d.lower() not in DEFAULT_IGNORE)
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            rel = relative_path(root, path)
            if any(fnmatch.fnmatchcase(rel, pattern) for pattern in excludes):
                continue
            if globs and not any(fnmatch.fnmatchcase(rel, pattern) for pattern in globs):
                continue
            try:
                if max_bytes > 0 and path.stat().st_size > max_bytes:
                    continue
            except OSError:
                stats['stat_error_count'] = int(stats['stat_error_count']) + 1
                paths = stats['stat_error_paths']
                if isinstance(paths, list) and len(paths) < ERROR_PATH_LIMIT:
                    paths.append(rel)
                continue
            yield path


def looks_binary(path: Path) -> bool:
    try:
        with path.open('rb') as handle:
            return b'\x00' in handle.read(4096)
    except OSError:
        return True


def portable_search(
    root: Path,
    pattern: str,
    ignore_case: bool,
    fixed_string: bool,
    globs: list[str],
    excludes: list[str],
    max_results: int,
    max_file_bytes: int,
    context: int,
) -> tuple[list[dict[str, object]], bool, dict[str, object]]:
    stats: dict[str, object] = {
        'walk_error_count': 0,
        'walk_error_paths': [],
        'stat_error_count': 0,
        'stat_error_paths': [],
        'read_error_count': 0,
        'read_error_paths': [],
    }
    flags = re.IGNORECASE if ignore_case else 0
    expression = re.escape(pattern) if fixed_string else pattern
    matcher = re.compile(expression, flags)
    matches: list[dict[str, object]] = []
    wanted = max_results + 1 if max_results > 0 else 0

    for path in iter_files(root, globs, excludes, max_file_bytes, stats):
        if looks_binary(path):
            continue
        try:
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            stats['read_error_count'] = int(stats['read_error_count']) + 1
            paths = stats['read_error_paths']
            if isinstance(paths, list) and len(paths) < ERROR_PATH_LIMIT:
                paths.append(relative_path(root, path))
            continue

        for index, line in enumerate(lines):
            if not matcher.search(line):
                continue
            item: dict[str, object] = {
                'path': relative_path(root, path),
                'line': index + 1,
                'text': line,
            }
            if context > 0:
                before = [
                    {'line': number + 1, 'text': lines[number]}
                    for number in range(max(0, index - context), index)
                ]
                after = [
                    {'line': number + 1, 'text': lines[number]}
                    for number in range(index + 1, min(len(lines), index + context + 1))
                ]
                if before:
                    item['before'] = before
                if after:
                    item['after'] = after
            matches.append(item)
            if wanted and len(matches) >= wanted:
                return matches[:max_results], True, stats

    return matches, False, stats


def rg_glob_args(globs: list[str], excludes: list[str]) -> list[str]:
    args: list[str] = []
    for name in sorted(DEFAULT_IGNORE):
        args.extend(['--glob', f'!**/{name}/**'])
    for pattern in globs:
        args.extend(['--glob', pattern])
    for pattern in excludes:
        args.extend(['--glob', f'!{pattern}'])
    return args


def ripgrep_search(
    executable: str,
    root: Path,
    pattern: str,
    ignore_case: bool,
    fixed_string: bool,
    globs: list[str],
    excludes: list[str],
    max_results: int,
    max_file_bytes: int,
) -> tuple[list[dict[str, object]], bool, str | None]:
    command = [executable, '--json', '--color', 'never', '--hidden', '--no-ignore']
    if ignore_case:
        command.append('--ignore-case')
    if fixed_string:
        command.append('--fixed-strings')
    if max_file_bytes > 0:
        command.extend(['--max-filesize', str(max_file_bytes)])
    command.extend(rg_glob_args(globs, excludes))
    command.extend(['--', pattern, '.'])

    process = subprocess.Popen(
        command,
        cwd=root,
        text=True,
        encoding='utf-8',
        errors='replace',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    matches: list[dict[str, object]] = []
    truncated = False
    wanted = max_results + 1 if max_results > 0 else 0
    assert process.stdout is not None

    try:
        for raw_line in process.stdout:
            try:
                message = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if message.get('type') != 'match':
                continue
            data = message.get('data') or {}
            path_data = data.get('path') or {}
            lines_data = data.get('lines') or {}
            path_text = path_data.get('text')
            line_number = data.get('line_number')
            text = lines_data.get('text')
            if not isinstance(path_text, str) or not isinstance(line_number, int) or not isinstance(text, str):
                continue
            path_text = path_text.replace('\\', '/').removeprefix('./')
            matches.append({'path': path_text, 'line': line_number, 'text': text.rstrip('\r\n')})
            if wanted and len(matches) >= wanted:
                truncated = True
                process.terminate()
                break
    finally:
        try:
            _, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            _, stderr = process.communicate()

    if truncated:
        return matches[:max_results], True, None
    if process.returncode not in (0, 1):
        return [], False, (stderr or 'ripgrep failed').strip()[:1200]
    return matches, False, None


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Search text and return compact self-describing JSON. Uses ripgrep when compatible and available.'
    )
    parser.add_argument('pattern')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('-i', '--ignore-case', action='store_true')
    parser.add_argument('-F', '--fixed-string', action='store_true')
    parser.add_argument('-g', '--glob', action='append', default=[])
    parser.add_argument('--exclude', action='append', default=[])
    parser.add_argument('--max-results', type=int, default=100, help='Maximum matches returned. 0 means unlimited.')
    parser.add_argument('--max-file-bytes', type=int, default=2_000_000, help='Skip larger files. 0 means unlimited.')
    parser.add_argument('--context', type=int, default=0, help='Context lines returned around each match.')
    parser.add_argument('--backend', choices=['auto', 'portable', 'ripgrep'], default='auto')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    query = {
        'pattern': args.pattern,
        'mode': 'fixed_string' if args.fixed_string else 'regex',
        'ignore_case': args.ignore_case,
        'globs': args.glob,
        'excludes': args.exclude,
        'context_lines': max(0, args.context),
    }
    if not root.exists():
        emit({'tool': TOOL, 'status': 'input_missing', 'root_path': str(root), 'query': query})
        return 2
    if not root.is_dir():
        emit({'tool': TOOL, 'status': 'input_not_directory', 'root_path': str(root), 'query': query})
        return 2
    if not args.fixed_string:
        regex_error = validate_regex(args.pattern)
        if regex_error:
            emit({'tool': TOOL, 'status': 'invalid_pattern', 'root_path': str(root), 'query': query, 'error': regex_error[:1200]})
            return 2

    max_results = normalize_limit(args.max_results)
    max_file_bytes = normalize_limit(args.max_file_bytes)
    context = normalize_limit(args.context)
    ripgrep = shutil.which('rg')
    can_use_rg = context == 0

    if args.backend == 'ripgrep' and not ripgrep:
        emit({'tool': TOOL, 'status': 'external_backend_unavailable', 'root_path': str(root), 'query': query, 'backend': 'ripgrep'})
        return 2
    if args.backend == 'ripgrep' and not can_use_rg:
        emit({'tool': TOOL, 'status': 'backend_query_unsupported', 'root_path': str(root), 'query': query, 'backend': 'ripgrep', 'unsupported_feature': 'context_lines'})
        return 2

    warning: dict[str, object] | None = None
    use_rg = args.backend == 'ripgrep' or (args.backend == 'auto' and ripgrep is not None and can_use_rg)
    if use_rg and ripgrep:
        matches, truncated, error = ripgrep_search(
            ripgrep, root, args.pattern, args.ignore_case, args.fixed_string,
            args.glob, args.exclude, max_results, max_file_bytes,
        )
        if error is None:
            emit({
                'tool': TOOL,
                'status': 'ok',
                'root_path': str(root),
                'query': query,
                'backend': 'ripgrep',
                'matches': matches,
                'matches_truncated': truncated,
            })
            return 0
        if args.backend == 'ripgrep':
            emit({'tool': TOOL, 'status': 'external_backend_failed', 'root_path': str(root), 'query': query, 'backend': 'ripgrep', 'error': error})
            return 2
        warning = {'backend': 'ripgrep', 'status': 'failed', 'error': error}

    matches, truncated, stats = portable_search(
        root, args.pattern, args.ignore_case, args.fixed_string, args.glob, args.exclude,
        max_results, max_file_bytes, context,
    )
    warning_count = int(stats['walk_error_count']) + int(stats['stat_error_count']) + int(stats['read_error_count'])
    payload: dict[str, object] = {
        'tool': TOOL,
        'status': 'partial' if warning_count else 'ok',
        'root_path': str(root),
        'query': query,
        'backend': 'portable',
        'matches': matches,
        'matches_truncated': truncated,
        'walk_error_count': stats['walk_error_count'],
        'stat_error_count': stats['stat_error_count'],
        'read_error_count': stats['read_error_count'],
    }
    if stats['walk_error_paths']:
        payload['walk_error_paths'] = stats['walk_error_paths']
    if stats['stat_error_paths']:
        payload['stat_error_paths'] = stats['stat_error_paths']
    if stats['read_error_paths']:
        payload['read_error_paths'] = stats['read_error_paths']
    if warning is not None:
        payload['backend_fallback'] = warning
        if payload['status'] == 'ok':
            payload['status'] = 'ok_with_backend_fallback'
    emit(payload)
    return 0


if __name__ == '__main__':
    sys.exit(main())
