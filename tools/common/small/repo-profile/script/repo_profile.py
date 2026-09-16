#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

TOOL = 'repo-profile'
IGNORE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor', 'generated',
}
LANG = {
    '.py': 'Python', '.cs': 'CSharp', '.go': 'Go', '.gd': 'GDScript',
    '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.hpp': 'C++', '.hh': 'C++', '.hxx': 'C++',
    '.c': 'C', '.h': 'C/C++ Header',
    '.rs': 'Rust', '.js': 'JavaScript', '.ts': 'TypeScript', '.java': 'Java',
}
ERROR_PATH_LIMIT = 20


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def walk(root: Path, max_files: int) -> tuple[list[Path], bool, dict[str, object]]:
    max_files = max(0, max_files)
    files: list[Path] = []
    stats: dict[str, object] = {'walk_error_count': 0, 'walk_error_paths': []}
    wanted = max_files + 1 if max_files > 0 else 0

    def on_error(error: OSError) -> None:
        stats['walk_error_count'] = int(stats['walk_error_count']) + 1
        paths = stats['walk_error_paths']
        if isinstance(paths, list) and len(paths) < ERROR_PATH_LIMIT:
            paths.append(str(getattr(error, 'filename', '') or 'unknown'))

    for current, dirs, names in os.walk(root, onerror=on_error):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        for name in sorted(names):
            files.append(Path(current) / name)
            if wanted and len(files) >= wanted:
                return files[:max_files], True, stats
    return files, False, stats


def portable_language_metrics(files: list[Path]) -> tuple[dict[str, int], list[dict[str, object]]]:
    languages = Counter()
    for path in files:
        language = LANG.get(path.suffix.lower())
        if language is not None:
            languages[language] += 1
    metrics = [
        {
            'language': language,
            'files': count,
            'lines': None,
            'code': None,
            'comment': None,
            'blank': None,
            'complexity': None,
        }
        for language, count in languages.most_common()
    ]
    return dict(languages.most_common()), metrics


def parse_scc_payload(payload: object) -> tuple[dict[str, int], list[dict[str, object]]]:
    if not isinstance(payload, list):
        raise ValueError('scc JSON output must be a language summary array')
    metrics: list[dict[str, object]] = []
    counts: dict[str, int] = {}
    for raw in payload:
        if not isinstance(raw, dict):
            continue
        name = raw.get('Name')
        count = raw.get('Count')
        if not isinstance(name, str) or not isinstance(count, int):
            continue
        counts[name] = count
        metrics.append({
            'language': name,
            'files': count,
            'lines': raw.get('Lines') if isinstance(raw.get('Lines'), int) else None,
            'code': raw.get('Code') if isinstance(raw.get('Code'), int) else None,
            'comment': raw.get('Comment') if isinstance(raw.get('Comment'), int) else None,
            'blank': raw.get('Blank') if isinstance(raw.get('Blank'), int) else None,
            'complexity': raw.get('Complexity') if isinstance(raw.get('Complexity'), int) else None,
        })
    metrics.sort(key=lambda row: (-int(row['files']), str(row['language']).lower()))
    counts = {row['language']: int(row['files']) for row in metrics}
    return counts, metrics


def run_scc(root: Path) -> tuple[dict[str, int] | None, list[dict[str, object]] | None, str | None]:
    executable = shutil.which('scc')
    if not executable:
        return None, None, 'scc executable was not found on PATH'
    command = [executable, '--format', 'json']
    for name in sorted(IGNORE - {'.git', '.hg', '.svn'}):
        command.extend(['--exclude-dir', name])
    command.append(str(root))
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return None, None, (result.stderr.strip() or 'scc failed')[:1200]
    try:
        payload = json.loads(result.stdout)
        counts, metrics = parse_scc_payload(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        return None, None, str(exc)[:1200]
    return counts, metrics, None


def build_profile(
    root: Path,
    max_files: int,
    backend: str = 'portable',
) -> dict[str, object]:
    files, truncated, stats = walk(root, max_files)
    portable_counts, portable_metrics = portable_language_metrics(files)
    selected_backend = 'portable'
    language_counts = portable_counts
    language_metrics = portable_metrics
    backend_fallback: dict[str, object] | None = None

    scc_available = shutil.which('scc') is not None
    should_try_scc = (
        max(0, max_files) == 0
        and (backend == 'scc' or (backend == 'auto' and scc_available))
    )
    if should_try_scc:
        counts, metrics, error = run_scc(root)
        if error is None and counts is not None and metrics is not None:
            selected_backend = 'scc'
            language_counts = counts
            language_metrics = metrics
        elif backend == 'scc':
            return {
                'tool': TOOL,
                'status': 'external_backend_unavailable' if not scc_available else 'external_backend_failed',
                'project_root': str(root),
                'backend': 'scc',
                'error': error,
            }
        else:
            backend_fallback = {'backend': 'scc', 'status': 'failed', 'error': error}
    elif backend == 'scc':
        return {
            'tool': TOOL,
            'status': 'external_backend_unavailable' if not scc_available else 'backend_query_unsupported',
            'project_root': str(root),
            'backend': 'scc',
            'error': 'scc executable was not found on PATH' if not scc_available else 'max_files is not supported by the scc backend',
        }

    recognized = sum(language_counts.values())
    non_language_files = max(0, len(files) - recognized)
    if truncated:
        size = 'large_or_unknown_due_to_scan_limit'
    else:
        size = 'small' if len(files) < 200 else 'medium' if len(files) < 2000 else 'large'

    top_dirs = set()
    for path in files:
        rel = path.relative_to(root)
        if len(rel.parts) > 1:
            top_dirs.add(rel.parts[0])

    warning_count = int(stats['walk_error_count'])
    status = 'partial' if warning_count or truncated else 'ok'
    if backend_fallback is not None and status == 'ok':
        status = 'ok_with_backend_fallback'
    result: dict[str, object] = {
        'tool': TOOL,
        'status': status,
        'project_root': str(root),
        'backend': selected_backend,
        'project_size_class': size,
        'files_scanned': len(files),
        'scan_truncated': truncated,
        'recognized_source_files_scanned': recognized,
        'non_language_files_scanned': non_language_files,
        'language_file_counts': language_counts,
        'language_metrics': language_metrics,
        'top_level_directories': sorted(top_dirs)[:30],
        'top_level_directories_truncated': len(top_dirs) > 30,
        'walk_error_count': stats['walk_error_count'],
    }
    if stats['walk_error_paths']:
        result['walk_error_paths'] = stats['walk_error_paths']
    if backend_fallback is not None:
        result['backend_fallback'] = backend_fallback
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description='Create a compact self-describing repository profile.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--max-files', type=int, default=0, help='Optional portable scan safety limit. 0 means unlimited.')
    parser.add_argument('--backend', choices=['auto', 'portable', 'scc'], default='auto')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        emit({'tool': TOOL, 'status': 'input_missing', 'project_root': str(root)})
        return 2
    if not root.is_dir():
        emit({'tool': TOOL, 'status': 'input_not_directory', 'project_root': str(root)})
        return 2
    if args.backend == 'scc' and max(0, args.max_files) > 0:
        emit({
            'tool': TOOL,
            'status': 'backend_query_unsupported',
            'project_root': str(root),
            'backend': 'scc',
            'unsupported_feature': 'max_files',
        })
        return 2

    result = build_profile(root, args.max_files, args.backend)
    emit(result)
    return 0 if result.get('status') not in {
        'external_backend_unavailable', 'external_backend_failed', 'backend_query_unsupported'
    } else 2


if __name__ == '__main__':
    sys.exit(main())
