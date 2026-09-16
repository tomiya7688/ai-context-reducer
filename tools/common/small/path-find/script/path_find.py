#!/usr/bin/env python3
"""Portable path finder with optional fd acceleration."""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = 'path-find'
IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor', 'generated',
}
ERROR_PATH_LIMIT = 20


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def normalized(path: str) -> str:
    value = path.replace('\\', '/').removeprefix('./')
    return value.rstrip('/')


def matches_pattern(name: str, rel: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(name, pattern) or fnmatch.fnmatchcase(rel, pattern)


def portable_find(
    root: Path,
    pattern: str,
    entry_type: str,
    max_results: int,
    max_depth: int,
    max_visited: int,
) -> tuple[list[dict[str, str]], bool, bool, dict[str, object]]:
    results: list[dict[str, str]] = []
    results_truncated = False
    scan_truncated = False
    visited = 0
    stats: dict[str, object] = {'walk_error_count': 0, 'walk_error_paths': []}
    wanted = max_results + 1 if max_results > 0 else 0

    def walk_error(error: OSError) -> None:
        stats['walk_error_count'] = int(stats['walk_error_count']) + 1
        paths = stats['walk_error_paths']
        if isinstance(paths, list) and len(paths) < ERROR_PATH_LIMIT:
            paths.append(str(getattr(error, 'filename', '') or 'unknown'))

    for current, dirs, files in os.walk(root, onerror=walk_error):
        rel_dir = Path(current).relative_to(root)
        depth = 0 if rel_dir == Path('.') else len(rel_dir.parts)
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        if max_depth > 0 and depth >= max_depth:
            dirs[:] = []

        entries: list[tuple[str, str]] = []
        if entry_type in {'dir', 'any'}:
            entries.extend((name, 'dir') for name in dirs)
        if entry_type in {'file', 'any'}:
            entries.extend((name, 'file') for name in sorted(files))

        for name, kind in entries:
            if max_visited > 0 and visited >= max_visited:
                scan_truncated = True
                return results[:max_results] if max_results > 0 else results, results_truncated, scan_truncated, stats
            visited += 1
            path = Path(current) / name
            rel = path.relative_to(root).as_posix()
            if max_depth > 0 and len(Path(rel).parts) > max_depth:
                continue
            if not matches_pattern(name, rel, pattern):
                continue
            results.append({'path': rel, 'kind': kind})
            if wanted and len(results) >= wanted:
                results_truncated = True
                return results[:max_results], results_truncated, scan_truncated, stats

    return results, results_truncated, scan_truncated, stats


def fd_find(
    executable: str,
    root: Path,
    pattern: str,
    entry_type: str,
    max_results: int,
    max_depth: int,
) -> tuple[list[dict[str, str]], bool, str | None]:
    command = [
        executable,
        '--glob',
        '--case-sensitive',
        '--hidden',
        '--no-ignore',
        '--color', 'never',
    ]
    if entry_type == 'file':
        command.extend(['--type', 'file'])
    elif entry_type == 'dir':
        command.extend(['--type', 'directory'])
    if max_depth > 0:
        command.extend(['--max-depth', str(max_depth)])
    for name in sorted(IGNORE):
        command.extend(['--exclude', name])
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
    results: list[dict[str, str]] = []
    truncated = False
    wanted = max_results + 1 if max_results > 0 else 0
    assert process.stdout is not None

    try:
        for raw_line in process.stdout:
            rel = normalized(raw_line.strip())
            if not rel:
                continue
            if entry_type == 'file':
                kind = 'file'
            elif entry_type == 'dir':
                kind = 'dir'
            else:
                kind = 'dir' if (root / rel).is_dir() else 'file'
            results.append({'path': rel, 'kind': kind})
            if wanted and len(results) >= wanted:
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
        return results[:max_results], True, None
    if process.returncode != 0:
        return [], False, (stderr or 'fd failed').strip()[:1200]
    return results, False, None


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Find paths and return compact self-describing JSON. Uses fd when compatible and available.'
    )
    parser.add_argument('pattern', nargs='?', default='*')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--type', choices=['file', 'dir', 'any'], default='file')
    parser.add_argument('--max-results', type=int, default=200, help='Maximum results returned. 0 means unlimited.')
    parser.add_argument('--max-depth', type=int, default=0, help='Maximum traversal depth. 0 means unlimited.')
    parser.add_argument('--max-visited', type=int, default=0, help='Portable-backend safety cap. 0 means unlimited.')
    parser.add_argument('--backend', choices=['auto', 'portable', 'fd'], default='auto')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    max_results = max(0, args.max_results)
    max_depth = max(0, args.max_depth)
    max_visited = max(0, args.max_visited)
    query = {'pattern': args.pattern, 'type': args.type, 'max_depth': max_depth}

    if not root.exists():
        emit({'tool': TOOL, 'status': 'input_missing', 'root_path': str(root), 'query': query})
        return 2
    if not root.is_dir():
        emit({'tool': TOOL, 'status': 'input_not_directory', 'root_path': str(root), 'query': query})
        return 2

    fd = shutil.which('fd')
    pattern_uses_path = '/' in args.pattern or '\\' in args.pattern
    can_use_fd = not pattern_uses_path and max_visited == 0

    if args.backend == 'fd' and not fd:
        emit({'tool': TOOL, 'status': 'external_backend_unavailable', 'root_path': str(root), 'query': query, 'backend': 'fd'})
        return 2
    if args.backend == 'fd' and not can_use_fd:
        unsupported = 'path_pattern' if pattern_uses_path else 'max_visited'
        emit({'tool': TOOL, 'status': 'backend_query_unsupported', 'root_path': str(root), 'query': query, 'backend': 'fd', 'unsupported_feature': unsupported})
        return 2

    warning: dict[str, object] | None = None
    use_fd = args.backend == 'fd' or (args.backend == 'auto' and fd is not None and can_use_fd)
    if use_fd and fd:
        results, truncated, error = fd_find(fd, root, args.pattern, args.type, max_results, max_depth)
        if error is None:
            emit({
                'tool': TOOL,
                'status': 'ok',
                'root_path': str(root),
                'query': query,
                'backend': 'fd',
                'results': results,
                'results_truncated': truncated,
                'scan_truncated': False,
            })
            return 0
        if args.backend == 'fd':
            emit({'tool': TOOL, 'status': 'external_backend_failed', 'root_path': str(root), 'query': query, 'backend': 'fd', 'error': error})
            return 2
        warning = {'backend': 'fd', 'status': 'failed', 'error': error}

    results, results_truncated, scan_truncated, stats = portable_find(
        root, args.pattern, args.type, max_results, max_depth, max_visited,
    )
    warning_count = int(stats['walk_error_count'])
    status = 'partial' if warning_count or scan_truncated else 'ok'
    if warning is not None and status == 'ok':
        status = 'ok_with_backend_fallback'
    payload: dict[str, object] = {
        'tool': TOOL,
        'status': status,
        'root_path': str(root),
        'query': query,
        'backend': 'portable',
        'results': results,
        'results_truncated': results_truncated,
        'scan_truncated': scan_truncated,
        'walk_error_count': stats['walk_error_count'],
    }
    if stats['walk_error_paths']:
        payload['walk_error_paths'] = stats['walk_error_paths']
    if warning is not None:
        payload['backend_fallback'] = warning
    emit(payload)
    return 0


if __name__ == '__main__':
    sys.exit(main())
