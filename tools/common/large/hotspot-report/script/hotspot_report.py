#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

SKIP = {
    '.git', '.hg', '.svn', 'node_modules', 'build', 'dist', 'bin', 'obj',
    '.venv', 'venv', '__pycache__', '.godot', '.idea', '.vs', 'vendor',
}


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Report large/deep repository hotspots as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=30)
    parser.add_argument('--max-files', type=int, default=0, help='Optional safety limit. 0 means unlimited.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        emit({'tool': 'hotspot-report', 'status': 'input_missing', 'root': str(root)})
        return
    if not root.is_dir():
        emit({'tool': 'hotspot-report', 'status': 'input_not_directory', 'root': str(root)})
        return

    rows = []
    scanned = 0
    scan_truncated = False
    stat_error_count = 0
    walk_error_count = 0

    def on_walk_error(_error):
        nonlocal walk_error_count
        walk_error_count += 1

    for current, dirs, files in os.walk(root, onerror=on_walk_error):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            try:
                size = path.stat().st_size
            except OSError:
                stat_error_count += 1
                continue
            rel = path.relative_to(root)
            rows.append({
                'path': rel.as_posix(),
                'bytes': size,
                'depth': len(rel.parts),
            })
            scanned += 1
            if args.max_files > 0 and scanned >= args.max_files:
                scan_truncated = True
                break
        if scan_truncated:
            break

    rows.sort(key=lambda row: (row['bytes'], row['depth'], row['path']), reverse=True)
    limit = max(0, args.limit)
    errors = stat_error_count + walk_error_count
    emit({
        'tool': 'hotspot-report',
        'status': 'ok_with_warnings' if errors else 'ok',
        'root': str(root),
        'scanned_file_count': scanned,
        'stat_error_count': stat_error_count,
        'walk_error_count': walk_error_count,
        'scan_truncated': scan_truncated,
        'hotspot_count': len(rows),
        'hotspots': rows[:limit] if limit > 0 else [],
        'hotspots_truncated': limit == 0 and bool(rows) or (limit > 0 and len(rows) > limit),
    })


if __name__ == '__main__':
    main()
