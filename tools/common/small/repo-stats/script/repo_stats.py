#!/usr/bin/env python3
"""Dependency-free compact repository language/line statistics."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

IGNORE = {'.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__', 'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs'}
LANG = {
    '.py': 'Python', '.cs': 'CSharp', '.go': 'Go', '.c': 'C',
    '.h': 'C/C++ Header', '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++',
    '.hpp': 'C++ Header', '.hh': 'C++ Header', '.gd': 'GDScript',
    '.rs': 'Rust', '.js': 'JavaScript', '.ts': 'TypeScript', '.java': 'Java',
    '.md': 'Markdown', '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
    '.toml': 'TOML', '.xml': 'XML', '.html': 'HTML', '.css': 'CSS',
}


def build_stats(root: Path, max_file_bytes: int) -> dict[str, object]:
    stats = defaultdict(lambda: {'file_count': 0, 'line_count': 0, 'byte_count': 0})
    oversized_file_count = 0
    read_error_count = 0
    binary_like_file_count = 0
    recognized_files_seen = 0

    for p in root.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in IGNORE for part in rel.parts):
            continue
        lang = LANG.get(p.suffix.lower())
        if not lang:
            continue
        recognized_files_seen += 1
        try:
            size = p.stat().st_size
            if max_file_bytes > 0 and size > max_file_bytes:
                oversized_file_count += 1
                continue
            raw = p.read_bytes()
        except OSError:
            read_error_count += 1
            continue
        if b'\x00' in raw[:4096]:
            binary_like_file_count += 1
            continue
        lines = raw.count(b'\n') + (1 if raw and not raw.endswith(b'\n') else 0)
        row = stats[lang]
        row['file_count'] += 1
        row['line_count'] += lines
        row['byte_count'] += size

    ordered = dict(sorted(stats.items(), key=lambda kv: (-kv[1]['line_count'], kv[0])))
    return {
        'tool': 'repo-stats',
        'status': 'ok',
        'project_root': str(root),
        'recognized_files_seen': recognized_files_seen,
        'analyzed_file_count': sum(v['file_count'] for v in stats.values()),
        'analyzed_line_count': sum(v['line_count'] for v in stats.values()),
        'oversized_file_count': oversized_file_count,
        'read_error_count': read_error_count,
        'binary_like_file_count': binary_like_file_count,
        'max_file_bytes': max_file_bytes,
        'languages': ordered,
    }


def main():
    ap = argparse.ArgumentParser(description='Compact repository file/line statistics as self-describing JSON.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--max-file-bytes', type=int, default=5_000_000, help='Per-file safety limit. 0 means unlimited.')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        out = {'tool': 'repo-stats', 'status': 'input_missing', 'project_root': str(root)}
    elif not root.is_dir():
        out = {'tool': 'repo-stats', 'status': 'input_not_directory', 'project_root': str(root)}
    else:
        out = build_stats(root, max(0, args.max_file_bytes))
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
