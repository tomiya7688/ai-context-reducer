#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from impact import affected_scope
from messenger import load_json, write_json
from outline_adapter import normalize_symbol_payload
from processing import build_index, expand, query_nodes, resolve_target

TOOL = 'source-structure-index'
FORMAT = 'acr-source-structure-index-v1'


def emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def load_index(path: str) -> dict:
    payload = load_json(path)
    if not isinstance(payload, dict) or payload.get('format') != FORMAT:
        raise ValueError(f'unsupported index format; expected {FORMAT}')
    return payload


def build_command(args: argparse.Namespace) -> int:
    if not args.symbols and not args.graph:
        emit({'tool': TOOL, 'status': 'no_inputs', 'required_input': '--symbols and/or --graph'})
        return 2

    symbol_payloads = []
    graph_payloads = []
    failures = []
    for path in args.symbols:
        try:
            symbol_payloads.append((path, normalize_symbol_payload(load_json(path))))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append({'path': path, 'error': str(exc)})
    for path in args.graph:
        try:
            graph_payloads.append((path, load_json(path)))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append({'path': path, 'error': str(exc)})

    if failures:
        emit({'tool': TOOL, 'status': 'input_read_failed', 'input_errors': failures})
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
    })
    return 0


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


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description='Build and query a reusable source-structure index without dumping the full index into agent context.'
    )
    sub = ap.add_subparsers(dest='command', required=True)

    build = sub.add_parser('build', help='Normalize language-specific symbol/graph JSON into a reusable common index.')
    build.add_argument('--symbols', action='append', default=[], metavar='JSON', help='Symbol JSON from a language-specific analyzer or ast-grep outline. Repeatable.')
    build.add_argument('--graph', action='append', default=[], metavar='JSON', help='Dependency/call graph JSON. Repeatable.')
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


def main() -> int:
    args = parser().parse_args()
    args.depth = max(0, getattr(args, 'depth', 0))
    args.max_nodes = max(0, getattr(args, 'max_nodes', 0))
    args.max_results = max(0, getattr(args, 'max_results', 0))
    args.max_candidates = max(1, getattr(args, 'max_candidates', 20))
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
