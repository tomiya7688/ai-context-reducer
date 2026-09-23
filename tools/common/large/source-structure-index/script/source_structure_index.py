#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ctags_adapter import normalize_ctags_rows
from impact import affected_scope
from messenger import ctags_json, load_json, load_json_lines, scip_print_json, write_json
from outline_adapter import normalize_symbol_payload
from processing import build_index, expand, query_nodes, resolve_target
from scip_adapter import normalize_scip_print

TOOL = 'source-structure-index'
FORMAT = 'acr-source-structure-index-v1'


# command結果を単一JSON契約で返し、textとJSONの二重表現を避ける。
def emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


# 保存済みindexを検証して読み込み、壊れた入力を空indexとして扱わない。
def load_index(path: str) -> dict:
    payload = load_json(path)
    if not isinstance(payload, dict) or payload.get('format') != FORMAT:
        raise ValueError(f'unsupported index format; expected {FORMAT}')
    return payload


# SCIP入力を共通build sourceへ追加し、backend由来warningも保持する。
def _append_scip_input(symbol_payloads, graph_payloads, metadata_rows, source: str, mode: str, payload: object) -> None:
    symbols, graph, metadata = normalize_scip_print(payload)
    symbol_payloads.append((f'{source}#scip-symbols', symbols))
    graph_payloads.append((f'{source}#scip-graph', graph))
    indexer = metadata.get('indexer') if isinstance(metadata.get('indexer'), dict) else {}
    metadata_rows.append({
        'source': source,
        'mode': mode,
        'document_count': metadata.get('document_count', 0),
        'defined_symbol_count': metadata.get('defined_symbol_count', 0),
        'indexer_name': indexer.get('name'),
        'indexer_version': indexer.get('version'),
    })


# ctags入力を共通build sourceへ追加し、backend失敗を完全なsymbol情報と誤認しない。
def _append_ctags_input(symbol_payloads, metadata_rows, source: str, mode: str, payload: object) -> None:
    symbols, metadata = normalize_ctags_rows(payload)
    symbol_payloads.append((f'{source}#ctags-symbols', symbols))
    metadata_rows.append({
        'source': source,
        'mode': mode,
        'tag_count': metadata.get('tag_count', 0),
        'file_count': metadata.get('file_count', 0),
        'skipped_row_count': metadata.get('skipped_row_count', 0),
        'languages': metadata.get('languages', []),
    })


# 複数symbol/dependency sourceを統合し、bounded indexと完全性signalを生成する。
def build_command(args: argparse.Namespace) -> int:
    if not args.symbols and not args.graph and not args.scip and not args.scip_json and not args.ctags_source and not args.ctags_json:
        emit({
            'tool': TOOL,
            'status': 'no_inputs',
            'required_input': '--symbols, --graph, --scip-json, --scip, --ctags-json, and/or --ctags-source',
        })
        return 2

    symbol_payloads = []
    graph_payloads = []
    failures = []
    scip_inputs = []
    ctags_inputs = []

    for path in args.symbols:
        try:
            symbol_payloads.append((path, normalize_symbol_payload(load_json(path))))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append({'path': path, 'input_kind': 'symbols', 'status': 'read_failed', 'error': str(exc)})
    for path in args.graph:
        try:
            graph_payloads.append((path, load_json(path)))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append({'path': path, 'input_kind': 'graph', 'status': 'read_failed', 'error': str(exc)})
    for path in args.scip_json:
        try:
            _append_scip_input(symbol_payloads, graph_payloads, scip_inputs, path, 'scip_print_json_file', load_json(path))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append({'path': path, 'input_kind': 'scip_json', 'status': 'read_failed', 'error': str(exc)})
    for path in args.scip:
        result = scip_print_json(path)
        if not result.get('ok'):
            failures.append({
                'path': path,
                'input_kind': 'scip_index',
                'status': result.get('status', 'read_failed'),
                'backend': result.get('backend', 'scip'),
                'error': result.get('error', 'SCIP backend failed'),
            })
            continue
        try:
            _append_scip_input(symbol_payloads, graph_payloads, scip_inputs, path, 'scip_cli', result.get('payload'))
        except ValueError as exc:
            failures.append({'path': path, 'input_kind': 'scip_index', 'status': 'invalid_backend_output', 'error': str(exc)})
    for path in args.ctags_json:
        try:
            _append_ctags_input(symbol_payloads, ctags_inputs, path, 'ctags_json_lines_file', load_json_lines(path))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append({'path': path, 'input_kind': 'ctags_json', 'status': 'read_failed', 'error': str(exc)})
    for path in args.ctags_source:
        result = ctags_json(path)
        if not result.get('ok'):
            failures.append({
                'path': path,
                'input_kind': 'ctags_source',
                'status': result.get('status', 'read_failed'),
                'backend': result.get('backend', 'ctags'),
                'error': result.get('error', 'ctags backend failed'),
            })
            continue
        try:
            _append_ctags_input(symbol_payloads, ctags_inputs, path, 'ctags_cli', result.get('payload'))
        except ValueError as exc:
            failures.append({'path': path, 'input_kind': 'ctags_source', 'status': 'invalid_backend_output', 'error': str(exc)})

    if failures:
        backend_unavailable = {'backend_unavailable', 'backend_incompatible'}
        status = 'external_backend_unavailable' if all(
            row.get('status') in backend_unavailable for row in failures
        ) else 'input_read_failed'
        emit({'tool': TOOL, 'status': status, 'input_errors': failures})
        return 2

    root = Path(args.root).resolve() if args.root else None
    index = build_index(symbol_payloads, graph_payloads, root)
    write_json(args.output, index)
    status = 'ok_with_warnings' if index['input_errors'] else 'ok'
    emit({
        'tool': TOOL,
        'status': status,
        'index_path': str(Path(args.output)),
        'format': index['format'],
        'node_count': len(index['nodes']),
        'edge_count': len(index['edges']),
        'input_truncated': index['input_truncated'],
        'input_errors': index['input_errors'],
        'scip_inputs': scip_inputs,
        'ctags_inputs': ctags_inputs,
    })
    return 0


# symbol queryをbounded候補へ変換し、対象探索の初期working setを狭める。
def query_command(args: argparse.Namespace) -> int:
    try:
        index = load_index(args.index)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        emit({'tool': TOOL, 'status': 'index_read_failed', 'index_path': args.index, 'error': str(exc)})
        return 2

    matches, truncated = query_nodes(index, args.pattern, args.max_results)
    emit({
        'tool': TOOL,
        'status': 'ok',
        'index_path': args.index,
        'pattern': args.pattern,
        'matches': matches,
        'matches_truncated': truncated,
        'index_input_truncated': bool(index.get('input_truncated')),
    })
    return 0


# 選択nodeの近傍だけを展開し、fan-out/cycleを含む必要最小限の構造を返す。
def expand_command(args: argparse.Namespace) -> int:
    try:
        index = load_index(args.index)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        emit({'tool': TOOL, 'status': 'index_read_failed', 'index_path': args.index, 'error': str(exc)})
        return 2

    status, matches = resolve_target(index, args.target)
    if status != 'ok':
        emit({
            'tool': TOOL,
            'status': status,
            'index_path': args.index,
            'target': args.target,
            'candidate_matches': matches[:args.max_candidates],
            'candidate_matches_truncated': len(matches) > args.max_candidates,
            'index_input_truncated': bool(index.get('input_truncated')),
        })
        return 1 if status == 'target_not_found' else 2

    result = expand(index, matches[0]['id'], args.depth, args.max_nodes, args.direction)
    emit({
        'tool': TOOL,
        'status': 'ok',
        'index_path': args.index,
        'target': args.target,
        'index_input_truncated': bool(index.get('input_truncated')),
        **result,
    })
    return 0


# 変更fileから影響候補を辿り、不完全情報では安全側のbroader scopeを示す。
def affected_command(args: argparse.Namespace) -> int:
    try:
        index = load_index(args.index)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        emit({'tool': TOOL, 'status': 'index_read_failed', 'index_path': args.index, 'error': str(exc)})
        return 2

    result = affected_scope(index, args.changed, args.max_results)
    emit({
        'tool': TOOL,
        'status': 'ok_with_uncertainty' if result['impact_uncertain'] else 'ok',
        'index_path': args.index,
        'index_input_truncated': bool(index.get('input_truncated')),
        **result,
    })
    return 0


# subcommandごとの入力境界を定義し、CLI contractを一箇所へ集約する。
def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description='Build and query a reusable source-structure index without dumping the full index into agent context.'
    )
    sub = ap.add_subparsers(dest='command', required=True)

    build = sub.add_parser('build', help='Normalize existing analyzer/index outputs into a reusable common index.')
    build.add_argument('--symbols', action='append', default=[], metavar='JSON', help='Symbol JSON from a language-specific analyzer or ast-grep outline. Repeatable.')
    build.add_argument('--graph', action='append', default=[], metavar='JSON', help='Dependency/call graph JSON. Repeatable.')
    build.add_argument('--scip-json', action='append', default=[], metavar='JSON', help='JSON previously produced by scip print --json. Repeatable.')
    build.add_argument('--scip', action='append', default=[], metavar='INDEX.SCIP', help='Existing SCIP index. Requires an already-installed scip CLI; nothing is auto-installed. Repeatable.')
    build.add_argument('--ctags-json', action='append', default=[], metavar='JSONL', help='Universal Ctags JSON Lines output. Repeatable.')
    build.add_argument('--ctags-source', action='append', default=[], metavar='PATH', help='Source file/directory to index with an already-installed Universal Ctags JSON backend. Nothing is auto-installed. Repeatable.')
    build.add_argument('--root', help='Optional repository root used to make absolute symbol paths relative.')
    build.add_argument('--output', required=True, help='Index file to write. The full index is not printed to stdout.')
    build.set_defaults(func=build_command)

    query = sub.add_parser('query', help='Find index nodes by id, name, qualified name, or path.')
    query.add_argument('index')
    query.add_argument('pattern')
    query.add_argument('--max-results', type=int, default=40, help='Maximum matches returned. 0 means unlimited.')
    query.set_defaults(func=query_command)

    neighborhood = sub.add_parser('expand', help='Return a bounded graph neighborhood around one target.')
    neighborhood.add_argument('index')
    neighborhood.add_argument('target')
    neighborhood.add_argument('--depth', type=int, default=1)
    neighborhood.add_argument('--max-nodes', type=int, default=80, help='Maximum nodes returned. 0 means unlimited.')
    neighborhood.add_argument('--direction', choices=['in', 'out', 'both'], default='both')
    neighborhood.add_argument('--max-candidates', type=int, default=20, help='Maximum candidates returned for an ambiguous target.')
    neighborhood.set_defaults(func=expand_command)

    affected = sub.add_parser('affected', help='Compute transitive dependent modules from changed files using the reusable dependency graph.')
    affected.add_argument('index')
    affected.add_argument('--changed', action='append', required=True, metavar='PATH', help='Changed repository-relative file path. Repeatable.')
    affected.add_argument('--max-results', type=int, default=80, help='Maximum affected modules returned to the caller. The internal dependency closure is still complete. 0 means unlimited.')
    affected.set_defaults(func=affected_command)
    return ap


# CLIを各routing処理へ接続し、失敗も含めて機械可読な結果として返す。
def main() -> int:
    args = parser().parse_args()
    args.depth = max(0, getattr(args, 'depth', 0))
    args.max_nodes = max(0, getattr(args, 'max_nodes', 0))
    args.max_results = max(0, getattr(args, 'max_results', 0))
    args.max_candidates = max(1, getattr(args, 'max_candidates', 20))
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
