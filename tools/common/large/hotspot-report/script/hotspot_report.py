#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

SKIP = {
    '.git', '.hg', '.svn', 'node_modules', 'build', 'dist', 'bin', 'obj',
    '.venv', 'venv', '__pycache__', '.godot', '.idea', '.vs', 'vendor',
}


def main():
    parser = argparse.ArgumentParser(description='Report large/deep repository hotspots as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=30)
    parser.add_argument('--max-files', type=int, default=0, help='Optional safety limit. 0 means unlimited.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(json.dumps({
            'tool': 'hotspot-report',
            'status': 'root_missing',
            'root': str(root),
        }, ensure_ascii=False, indent=2))
        return

    rows = []
    scanned = 0
    scan_truncated = False
    stat_error_count = 0

    for current, dirs, files in os.walk(root):
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
    print(json.dumps({
        'tool': 'hotspot-report',
        'status': 'ok',
        'root': str(root),
        'scanned_file_count': scanned,
        'stat_error_count': stat_error_count,
        'scan_truncated': scan_truncated,
        'hotspot_count': len(rows),
        'hotspots': rows[:args.limit],
        'hotspots_truncated': len(rows) > args.limit,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
