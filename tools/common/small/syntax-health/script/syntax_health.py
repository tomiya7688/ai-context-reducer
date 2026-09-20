#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = 'syntax-health'


# emit は内部結果を安定した利用者向け表現へ変換する。
def emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


# int_value はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def int_value(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    return value if isinstance(value, int) else 0


# normalize_rows は表記揺れを正規化し、後段の比較条件を単純化する。
def normalize_rows(payload: object) -> list[dict[str, object]]:
    raw_rows = payload if isinstance(payload, list) else [payload]
    rows: list[dict[str, object]] = []
    for raw in raw_rows:
        if not isinstance(raw, dict):
            continue
        path = raw.get('path', raw.get('file', raw.get('filename', '')))
        if not isinstance(path, str):
            path = ''
        error_count = int_value(raw.get('error_count', raw.get('errors', 0)))
        missing_count = int_value(raw.get('missing_count', raw.get('missing', 0)))
        success = raw.get('successful', raw.get('success'))
        if isinstance(success, bool):
            ok = success and error_count == 0 and missing_count == 0
        else:
            ok = error_count == 0 and missing_count == 0
        rows.append({
            'path': path,
            'syntax_ok': ok,
            'error_count': error_count,
            'missing_count': missing_count,
        })
    rows.sort(key=lambda row: (bool(row['syntax_ok']), str(row['path'])))
    return rows


# summarize はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def summarize(payload: object, max_files: int) -> dict[str, object]:
    rows = normalize_rows(payload)
    failing = [row for row in rows if not row['syntax_ok']]
    limit = max(0, max_files)
    returned = failing if limit == 0 else failing[:limit]
    return {
        'tool': TOOL,
        'status': 'ok',
        'backend': 'tree-sitter-summary',
        'files_seen': len(rows),
        'files_with_syntax_issues': len(failing),
        'syntax_issue_files': returned,
        'syntax_issue_files_truncated': limit > 0 and len(failing) > limit,
    }


# run_tree_sitter はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def run_tree_sitter(targets: list[str]) -> tuple[object | None, str | None, str]:
    executable = shutil.which('tree-sitter')
    if executable is None:
        return None, 'tree-sitter executable was not found on PATH', 'unavailable'
    result = subprocess.run(
        [executable, 'parse', '--json-summary', *targets],
        text=True, capture_output=True, check=False,
    )
    if result.returncode != 0 and not result.stdout.strip():
        return None, (result.stderr.strip() or 'tree-sitter parse failed')[:1200], 'failed'
    try:
        return json.loads(result.stdout), None, 'ok'
    except json.JSONDecodeError as exc:
        return None, str(exc)[:1200], 'failed'


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main() -> int:
    parser = argparse.ArgumentParser(description='Compact Tree-sitter parse health as self-describing JSON.')
    parser.add_argument('targets', nargs='*', help='Files/directories passed to tree-sitter parse.')
    parser.add_argument('--json-input', help='Read a saved tree-sitter --json-summary file instead of executing tree-sitter.')
    parser.add_argument('--max-files', type=int, default=80, help='Maximum failing files returned. 0 means unlimited.')
    args = parser.parse_args()

    if args.json_input:
        source = Path(args.json_input)
        if not source.exists():
            emit({'tool': TOOL, 'status': 'input_missing', 'input_path': str(source)})
            return 2
        try:
            payload = json.loads(source.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            emit({'tool': TOOL, 'status': 'input_read_failed', 'input_path': str(source), 'error': str(exc)[:1200]})
            return 2
    else:
        if not args.targets:
            emit({'tool': TOOL, 'status': 'invalid_arguments', 'missing_argument': 'targets_or_json_input'})
            return 2
        payload, error, backend_status = run_tree_sitter(args.targets)
        if payload is None:
            emit({'tool': TOOL, 'status': 'external_backend_unavailable' if backend_status == 'unavailable' else 'external_backend_failed', 'backend': 'tree-sitter', 'error': error})
            return 2

    emit(summarize(payload, args.max_files))
    return 0


if __name__ == '__main__':
    sys.exit(main())
