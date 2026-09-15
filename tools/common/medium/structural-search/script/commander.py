from __future__ import annotations

from pathlib import Path

from messenger import find_ast_grep, run_ast_grep
from processing import PatternError, normalize_ast_grep_matches, python_ast_search


def search_structure(root: Path, pattern: str, language: str | None, max_results: int, backend: str) -> dict:
    base = {
        'tool': 'structural-search',
        'project_root': str(root),
        'pattern': pattern,
        'requested_language': language,
        'requested_backend': backend,
        'max_results': max_results,
    }

    if not root.exists():
        return {**base, 'status': 'input_missing', 'backend': None}
    if not root.is_dir():
        return {**base, 'status': 'input_not_directory', 'backend': None}

    executable = find_ast_grep() if backend in {'auto', 'ast-grep'} else None
    if executable:
        ok, rows, diagnostic = run_ast_grep(executable, root, pattern, language)
        if not ok:
            return {
                **base,
                'status': 'search_failed',
                'backend': 'ast-grep',
                'match_semantics': 'ast-grep-pattern',
                'diagnostic': diagnostic,
            }
        matches, truncated = normalize_ast_grep_matches(rows, max_results)
        return {
            **base,
            'status': 'ok',
            'backend': 'ast-grep',
            'match_semantics': 'ast-grep-pattern',
            'match_count': len(rows),
            'matches_returned': len(matches),
            'matches_truncated': truncated,
            'matches': matches,
        }

    if backend == 'ast-grep':
        return {
            **base,
            'status': 'backend_unavailable',
            'backend': None,
            'available_fallback_languages': ['python'],
        }

    if language and language.casefold() not in {'python', 'py'}:
        return {
            **base,
            'status': 'backend_unavailable_for_language',
            'backend': None,
            'available_fallback_languages': ['python'],
        }

    try:
        fallback = python_ast_search(root, pattern, max_results)
    except PatternError as exc:
        return {
            **base,
            'status': 'invalid_pattern',
            'backend': 'python-ast-fallback',
            'match_semantics': 'python-ast-single-node-pattern',
            'fallback_limitations': [
                'Python source only',
                'single statement or expression pattern',
                'single-node metavariables such as $ARG',
                'no variadic $$$ metavariables',
            ],
            'diagnostic': str(exc),
        }

    return {
        **base,
        'status': 'ok',
        'backend': 'python-ast-fallback',
        'match_semantics': 'python-ast-single-node-pattern',
        'fallback_limitations': [
            'Python source only',
            'single statement or expression pattern',
            'single-node metavariables such as $ARG',
            'no variadic $$$ metavariables',
        ],
        **fallback,
        'matches_returned': len(fallback['matches']),
    }
