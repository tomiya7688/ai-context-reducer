#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = 'git-history-health'
ERROR_LIMIT = 1200


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def bounded(text: str) -> str:
    text = text.strip()
    return text if len(text) <= ERROR_LIMIT else text[:ERROR_LIMIT]


def collect_metrics(node: object, prefix: str = '') -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    if isinstance(node, dict):
        level = node.get('levelOfConcern')
        value = node.get('value')
        if isinstance(level, (int, float)) and isinstance(value, (int, float)):
            item: dict[str, object] = {
                'metric': prefix or 'unknown',
                'value': value,
                'level_of_concern': level,
            }
            for source, target in (
                ('unit', 'unit'),
                ('description', 'description'),
                ('objectDescription', 'object_description'),
            ):
                raw = node.get(source)
                if isinstance(raw, str) and raw:
                    item[target] = raw
            out.append(item)
        for key, value_node in node.items():
            if key in {'value', 'levelOfConcern', 'unit', 'description', 'referenceValue', 'prefixes', 'objectName', 'objectDescription'}:
                continue
            child = f'{prefix}.{key}' if prefix else str(key)
            out.extend(collect_metrics(value_node, child))
    elif isinstance(node, list):
        for index, value_node in enumerate(node):
            child = f'{prefix}[{index}]' if prefix else f'[{index}]'
            out.extend(collect_metrics(value_node, child))
    return out


def summarize(payload: object, min_concern: float, max_findings: int) -> dict[str, object]:
    metrics = collect_metrics(payload)
    concerning = [row for row in metrics if float(row['level_of_concern']) >= min_concern]
    concerning.sort(key=lambda row: (-float(row['level_of_concern']), str(row['metric'])))
    limit = max(0, max_findings)
    returned = concerning if limit == 0 else concerning[:limit]
    return {
        'metric_count_total': len(metrics),
        'concern_count_total': len(concerning),
        'min_level_of_concern': min_concern,
        'findings': returned,
        'findings_truncated': limit > 0 and len(concerning) > limit,
    }


def run_git_sizer(root: Path) -> tuple[object | None, str | None, str]:
    executable = shutil.which('git-sizer')
    if not executable:
        return None, None, 'unavailable'
    result = subprocess.run(
        [executable, '--json', '--json-version=2', '--no-progress'],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None, bounded(result.stderr or result.stdout or 'git-sizer failed'), 'failed'
    try:
        return json.loads(result.stdout), None, 'ok'
    except json.JSONDecodeError as exc:
        return None, bounded(str(exc)), 'failed'


def main() -> int:
    parser = argparse.ArgumentParser(description='Compress git-sizer JSON into bounded repository-history health findings.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--json-input', help='Read saved git-sizer JSON instead of invoking git-sizer.')
    parser.add_argument('--min-concern', type=float, default=1.0)
    parser.add_argument('--max-findings', type=int, default=30, help='Maximum returned findings; 0 means unlimited.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        emit({'tool': TOOL, 'status': 'input_missing', 'project_root': str(root)})
        return 2
    if not root.is_dir():
        emit({'tool': TOOL, 'status': 'input_not_directory', 'project_root': str(root)})
        return 2

    backend = 'git-sizer-json-input' if args.json_input else 'git-sizer'
    if args.json_input:
        path = Path(args.json_input).resolve()
        if not path.exists():
            emit({'tool': TOOL, 'status': 'input_missing', 'project_root': str(root), 'backend': backend, 'json_input': str(path)})
            return 2
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            emit({'tool': TOOL, 'status': 'input_invalid', 'project_root': str(root), 'backend': backend, 'error': bounded(str(exc))})
            return 2
    else:
        payload, error, state = run_git_sizer(root)
        if state != 'ok':
            result: dict[str, object] = {
                'tool': TOOL,
                'status': 'external_backend_unavailable' if state == 'unavailable' else 'external_backend_failed',
                'project_root': str(root),
                'backend': backend,
            }
            if error:
                result['error'] = error
            emit(result)
            return 2

    result = {
        'tool': TOOL,
        'status': 'ok',
        'project_root': str(root),
        'backend': backend,
        **summarize(payload, max(0.0, args.min_concern), args.max_findings),
    }
    emit(result)
    return 0


if __name__ == '__main__':
    sys.exit(main())
