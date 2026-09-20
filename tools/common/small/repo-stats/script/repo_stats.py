#!/usr/bin/env python3
"""Compact repository language/line statistics with optional scc acceleration."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

TOOL = 'repo-stats'
IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor', 'generated',
}
LANG = {
    '.py': 'Python', '.cs': 'CSharp', '.go': 'Go', '.c': 'C',
    '.h': 'C/C++ Header', '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++',
    '.hpp': 'C++ Header', '.hh': 'C++ Header', '.gd': 'GDScript',
    '.rs': 'Rust', '.js': 'JavaScript', '.ts': 'TypeScript', '.java': 'Java',
    '.md': 'Markdown', '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
    '.toml': 'TOML', '.xml': 'XML', '.html': 'HTML', '.css': 'CSS',
}
ERROR_PATH_LIMIT = 20


# emit は内部結果を安定した利用者向け表現へ変換する。
def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


# empty_language_row はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def empty_language_row() -> dict[str, int | None]:
    return {
        'file_count': 0,
        'line_count': 0,
        'byte_count': 0,
        'code_count': None,
        'comment_count': None,
        'blank_count': None,
        'complexity': None,
    }


# build_portable_stats は解析結果を後段で再利用できる構造へ組み立てる。
def build_portable_stats(root: Path, max_file_bytes: int) -> dict[str, object]:
    max_file_bytes = max(0, max_file_bytes)
    stats: dict[str, dict[str, int | None]] = defaultdict(empty_language_row)
    oversized_file_count = 0
    read_error_count = 0
    read_error_paths: list[str] = []
    walk_error_count = 0
    walk_error_paths: list[str] = []
    binary_like_file_count = 0
    recognized_files_seen = 0

    # walk_error は対象scopeを調べ、routingに必要な情報だけを集める。
    def walk_error(error: OSError) -> None:
        nonlocal walk_error_count
        walk_error_count += 1
        if len(walk_error_paths) < ERROR_PATH_LIMIT:
            walk_error_paths.append(str(getattr(error, 'filename', '') or 'unknown'))

    for current, dirs, names in os.walk(root, onerror=walk_error):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        current_path = Path(current)
        for name in sorted(names):
            path = current_path / name
            lang = LANG.get(path.suffix.lower())
            if not lang:
                continue
            recognized_files_seen += 1
            rel = path.relative_to(root).as_posix()
            try:
                size = path.stat().st_size
                if max_file_bytes > 0 and size > max_file_bytes:
                    oversized_file_count += 1
                    continue
                raw = path.read_bytes()
            except OSError:
                read_error_count += 1
                if len(read_error_paths) < ERROR_PATH_LIMIT:
                    read_error_paths.append(rel)
                continue
            if b'\x00' in raw[:4096]:
                binary_like_file_count += 1
                continue
            lines = raw.count(b'\n') + (1 if raw and not raw.endswith(b'\n') else 0)
            row = stats[lang]
            row['file_count'] = int(row['file_count'] or 0) + 1
            row['line_count'] = int(row['line_count'] or 0) + lines
            row['byte_count'] = int(row['byte_count'] or 0) + size

    ordered = dict(sorted(stats.items(), key=lambda kv: (-int(kv[1]['line_count'] or 0), kv[0])))
    warning_count = walk_error_count + read_error_count
    payload: dict[str, object] = {
        'tool': TOOL,
        'status': 'partial' if warning_count else 'ok',
        'project_root': str(root),
        'backend': 'portable',
        'recognized_files_seen': recognized_files_seen,
        'analyzed_file_count': sum(int(v['file_count'] or 0) for v in stats.values()),
        'analyzed_line_count': sum(int(v['line_count'] or 0) for v in stats.values()),
        'oversized_file_count': oversized_file_count,
        'read_error_count': read_error_count,
        'walk_error_count': walk_error_count,
        'binary_like_file_count': binary_like_file_count,
        'max_file_bytes': max_file_bytes,
        'languages': ordered,
    }
    if read_error_paths:
        payload['read_error_paths'] = read_error_paths
    if walk_error_paths:
        payload['walk_error_paths'] = walk_error_paths
    return payload


# parse_scc_stats は外部入力を内部表現へ変換し、不正な値を後段へ流さない。
def parse_scc_stats(payload: object) -> dict[str, object]:
    if not isinstance(payload, list):
        raise ValueError('scc JSON output must be a language summary array')
    rows: list[tuple[str, dict[str, int | None]]] = []
    for raw in payload:
        if not isinstance(raw, dict):
            continue
        name = raw.get('Name')
        count = raw.get('Count')
        lines = raw.get('Lines')
        byte_count = raw.get('Bytes')
        if not isinstance(name, str) or not isinstance(count, int) or not isinstance(lines, int):
            continue
        row: dict[str, int | None] = {
            'file_count': count,
            'line_count': lines,
            'byte_count': byte_count if isinstance(byte_count, int) else 0,
            'code_count': raw.get('Code') if isinstance(raw.get('Code'), int) else None,
            'comment_count': raw.get('Comment') if isinstance(raw.get('Comment'), int) else None,
            'blank_count': raw.get('Blank') if isinstance(raw.get('Blank'), int) else None,
            'complexity': raw.get('Complexity') if isinstance(raw.get('Complexity'), int) else None,
        }
        rows.append((name, row))
    rows.sort(key=lambda item: (-int(item[1]['line_count'] or 0), item[0]))
    languages = dict(rows)
    return {
        'recognized_files_seen': sum(int(row['file_count'] or 0) for _, row in rows),
        'analyzed_file_count': sum(int(row['file_count'] or 0) for _, row in rows),
        'analyzed_line_count': sum(int(row['line_count'] or 0) for _, row in rows),
        'languages': languages,
    }


# run_scc はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def run_scc(root: Path) -> tuple[dict[str, object] | None, str | None, str]:
    executable = shutil.which('scc')
    if not executable:
        return None, 'scc executable was not found on PATH', 'unavailable'
    command = [executable, '--format', 'json']
    for name in sorted(IGNORE - {'.git', '.hg', '.svn'}):
        command.extend(['--exclude-dir', name])
    command.append(str(root))
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return None, (result.stderr.strip() or 'scc failed')[:1200], 'failed'
    try:
        parsed = parse_scc_stats(json.loads(result.stdout))
    except (json.JSONDecodeError, ValueError) as exc:
        return None, str(exc)[:1200], 'failed'
    return parsed, None, 'ok'


# build_stats は解析結果を後段で再利用できる構造へ組み立てる。
def build_stats(root: Path, max_file_bytes: int, backend: str = 'portable') -> dict[str, object]:
    max_file_bytes = max(0, max_file_bytes)
    scc_available = shutil.which('scc') is not None
    should_try_scc = (
        max_file_bytes == 0
        and (backend == 'scc' or (backend == 'auto' and scc_available))
    )
    if should_try_scc:
        scc_stats, error, backend_status = run_scc(root)
        if scc_stats is not None:
            return {
                'tool': TOOL,
                'status': 'ok',
                'project_root': str(root),
                'backend': 'scc',
                **scc_stats,
                'oversized_file_count': 0,
                'read_error_count': 0,
                'walk_error_count': 0,
                'binary_like_file_count': 0,
                'max_file_bytes': 0,
            }
        if backend == 'scc':
            return {
                'tool': TOOL,
                'status': 'external_backend_unavailable' if backend_status == 'unavailable' else 'external_backend_failed',
                'project_root': str(root),
                'backend': 'scc',
                'error': error,
            }
        portable = build_portable_stats(root, max_file_bytes)
        portable['status'] = 'partial' if portable['status'] == 'partial' else 'ok_with_backend_fallback'
        portable['backend_fallback'] = {'backend': 'scc', 'status': 'failed', 'error': error}
        return portable
    if backend == 'scc':
        return {
            'tool': TOOL,
            'status': 'external_backend_unavailable' if not scc_available else 'backend_query_unsupported',
            'project_root': str(root),
            'backend': 'scc',
            'error': 'scc executable was not found on PATH' if not scc_available else 'max_file_bytes is not supported by the scc backend',
        }
    return build_portable_stats(root, max_file_bytes)


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main() -> int:
    parser = argparse.ArgumentParser(description='Compact repository language/line statistics as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--max-file-bytes', type=int, default=0, help='Per-file portable safety limit. 0 means unlimited.')
    parser.add_argument('--backend', choices=['auto', 'portable', 'scc'], default='auto')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        emit({'tool': TOOL, 'status': 'input_missing', 'project_root': str(root)})
        return 2
    if not root.is_dir():
        emit({'tool': TOOL, 'status': 'input_not_directory', 'project_root': str(root)})
        return 2
    if args.backend == 'scc' and max(0, args.max_file_bytes) > 0:
        emit({
            'tool': TOOL,
            'status': 'backend_query_unsupported',
            'project_root': str(root),
            'backend': 'scc',
            'unsupported_feature': 'max_file_bytes',
        })
        return 2

    result = build_stats(root, args.max_file_bytes, args.backend)
    emit(result)
    return 2 if result.get('status') in {
        'external_backend_unavailable', 'external_backend_failed', 'backend_query_unsupported'
    } else 0


if __name__ == '__main__':
    sys.exit(main())
