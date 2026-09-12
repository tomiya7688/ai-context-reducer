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


def main():
    ap = argparse.ArgumentParser(description='Compact repository file/line statistics.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--max-file-bytes', type=int, default=5_000_000)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    stats = defaultdict(lambda: {'files': 0, 'lines': 0, 'bytes': 0})
    skipped = 0

    for p in root.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in IGNORE for part in rel.parts):
            continue
        lang = LANG.get(p.suffix.lower())
        if not lang:
            continue
        try:
            size = p.stat().st_size
            if size > args.max_file_bytes:
                skipped += 1
                continue
            raw = p.read_bytes()
        except OSError:
            skipped += 1
            continue
        if b'\x00' in raw[:4096]:
            skipped += 1
            continue
        lines = raw.count(b'\n') + (1 if raw and not raw.endswith(b'\n') else 0)
        row = stats[lang]
        row['files'] += 1
        row['lines'] += lines
        row['bytes'] += size

    ordered = dict(sorted(stats.items(), key=lambda kv: (-kv[1]['lines'], kv[0])))
    out = {
        'root': root.name,
        'total_files': sum(v['files'] for v in stats.values()),
        'total_lines': sum(v['lines'] for v in stats.values()),
        'skipped_files': skipped,
        'languages': ordered,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"files={out['total_files']} lines={out['total_lines']} skipped={skipped}")
        for lang, row in ordered.items():
            print(f"{lang}: files={row['files']} lines={row['lines']} bytes={row['bytes']}")


if __name__ == '__main__':
    main()
