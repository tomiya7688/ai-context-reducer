#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from messenger import collect_files
from processing import build_manifest


# manifestを単一JSON契約で出力し、AIが同じ情報をtextとJSONの両方から読む冗長性を避ける。
def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


# CLI入力を検証し、boundedなmanifest生成結果と明示的failureを同じ契約で返す。
def main() -> int:
    parser = argparse.ArgumentParser(description='Build a prioritized context manifest as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--limit', type=int, default=400, help='Maximum files returned. 0 returns no file rows while still scanning the full scope.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        emit({'tool': 'context-manifest', 'status': 'input_missing', 'root_path': str(root)})
        return 2
    if not root.is_dir():
        emit({'tool': 'context-manifest', 'status': 'input_not_directory', 'root_path': str(root)})
        return 2

    entries, scan_stats = collect_files(root)
    result = build_manifest(
        entries,
        max(0, args.limit),
        scan_stats['stat_error_count'],
        scan_stats['walk_error_count'],
    )
    result['root_path'] = str(root)
    emit(result)
    return 0


if __name__ == '__main__':
    sys.exit(main())
