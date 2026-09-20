from __future__ import annotations

import ast
import os
import re
from pathlib import Path

IGNORE = {'.git', '.venv', 'venv', 'node_modules', 'build', 'dist', 'bin', 'obj', '__pycache__', 'vendor'}
META_PREFIX = '__ACR_META_'
META_RE = re.compile(r'\$([A-Za-z_][A-Za-z0-9_]*)')
TEXT_LIMIT = 240
CAPTURE_TEXT_LIMIT = 120


class PatternError(ValueError):
    pass


# _bounded_text はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def _bounded_text(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit], True


# normalize_ast_grep_matches は表記揺れを正規化し、後段の比較条件を単純化する。
def normalize_ast_grep_matches(rows: list[dict], max_results: int) -> tuple[list[dict], bool]:
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        raw_range = row.get('range') or {}
        start = raw_range.get('start') or {}
        end = raw_range.get('end') or {}
        text, text_truncated = _bounded_text(str(row.get('text', '')), TEXT_LIMIT)
        match = {
            'path': str(row.get('file', '')),
            'language': row.get('language'),
            'start_line_1_based': int(start.get('line', 0)) + 1,
            'start_column_0_based': int(start.get('column', 0)),
            'end_line_1_based': int(end.get('line', 0)) + 1,
            'end_column_0_based': int(end.get('column', 0)),
            'matched_text': text,
            'matched_text_truncated': text_truncated,
        }
        captures = {}
        single = ((row.get('metaVariables') or {}).get('single') or {})
        if isinstance(single, dict):
            for name, value in sorted(single.items()):
                if not isinstance(value, dict):
                    continue
                capture_text, capture_truncated = _bounded_text(str(value.get('text', '')), CAPTURE_TEXT_LIMIT)
                captures[name] = {
                    'text': capture_text,
                    'text_truncated': capture_truncated,
                }
        if captures:
            match['captures'] = captures
        normalized.append(match)
    truncated = max_results > 0 and len(normalized) > max_results
    if max_results > 0:
        normalized = normalized[:max_results]
    return normalized, truncated


# _prepare_python_pattern はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def _prepare_python_pattern(pattern: str) -> ast.AST:
    if '$$$' in pattern:
        raise PatternError('variadic_metavariables_require_ast_grep_backend')
    prepared = META_RE.sub(lambda m: META_PREFIX + m.group(1), pattern)
    try:
        tree = ast.parse(prepared)
    except SyntaxError as exc:
        raise PatternError('pattern_is_not_valid_python_after_metavariable_substitution') from exc
    if len(tree.body) != 1:
        raise PatternError('fallback_pattern_must_contain_one_python_statement_or_expression')
    node = tree.body[0]
    return node.value if isinstance(node, ast.Expr) else node


# _meta_name はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def _meta_name(value: object) -> str | None:
    if isinstance(value, ast.Name) and value.id.startswith(META_PREFIX):
        return value.id[len(META_PREFIX):]
    if isinstance(value, str) and value.startswith(META_PREFIX):
        return value[len(META_PREFIX):]
    return None


# _capture_signature はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def _capture_signature(value: object) -> object:
    if isinstance(value, ast.AST):
        return ast.dump(value, include_attributes=False)
    return value


# _matches はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def _matches(pattern: object, candidate: object, captures: dict[str, object]) -> bool:
    meta = _meta_name(pattern)
    if meta is not None:
        previous = captures.get(meta)
        if previous is None:
            captures[meta] = candidate
            return True
        return _capture_signature(previous) == _capture_signature(candidate)

    if isinstance(pattern, ast.AST):
        if not isinstance(candidate, type(pattern)):
            return False
        for field, pattern_value in ast.iter_fields(pattern):
            if field in {'ctx', 'type_comment'}:
                continue
            if not _matches(pattern_value, getattr(candidate, field, None), captures):
                return False
        return True
    if isinstance(pattern, list):
        if not isinstance(candidate, list) or len(pattern) != len(candidate):
            return False
        return all(_matches(p, c, captures) for p, c in zip(pattern, candidate))
    return pattern == candidate


# _capture_text はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def _capture_text(source: str, value: object) -> dict:
    if isinstance(value, ast.AST):
        raw = ast.get_source_segment(source, value) or ''
    else:
        raw = str(value)
    text, truncated = _bounded_text(raw, CAPTURE_TEXT_LIMIT)
    return {'text': text, 'text_truncated': truncated}


# _candidate_match はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def _candidate_match(path: Path, root: Path, source: str, node: ast.AST, captures: dict[str, object]) -> dict:
    raw = ast.get_source_segment(source, node) or ''
    text, text_truncated = _bounded_text(raw, TEXT_LIMIT)
    match = {
        'path': path.relative_to(root).as_posix(),
        'language': 'Python',
        'start_line_1_based': int(getattr(node, 'lineno', 1)),
        'start_column_0_based': int(getattr(node, 'col_offset', 0)),
        'end_line_1_based': int(getattr(node, 'end_lineno', getattr(node, 'lineno', 1))),
        'end_column_0_based': int(getattr(node, 'end_col_offset', 0)),
        'matched_text': text,
        'matched_text_truncated': text_truncated,
    }
    if captures:
        match['captures'] = {
            name: _capture_text(source, value)
            for name, value in sorted(captures.items())
        }
    return match


# python_ast_search はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def python_ast_search(root: Path, pattern: str, max_results: int) -> dict:
    pattern_node = _prepare_python_pattern(pattern)
    matches = []
    files_scanned = 0
    parse_error_paths = []
    parse_error_count = 0

    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        current_path = Path(current)
        for name in sorted(names):
            if not name.lower().endswith('.py'):
                continue
            path = current_path / name
            files_scanned += 1
            try:
                source = path.read_text(encoding='utf-8', errors='replace')
                tree = ast.parse(source)
            except (OSError, SyntaxError):
                parse_error_count += 1
                if len(parse_error_paths) < 20:
                    parse_error_paths.append(path.relative_to(root).as_posix())
                continue
            for node in ast.walk(tree):
                captures: dict[str, object] = {}
                if _matches(pattern_node, node, captures):
                    matches.append(_candidate_match(path, root, source, node, captures))

    truncated = max_results > 0 and len(matches) > max_results
    returned = matches[:max_results] if max_results > 0 else matches
    return {
        'matches': returned,
        'match_count': len(matches),
        'matches_truncated': truncated,
        'files_scanned': files_scanned,
        'parse_error_count': parse_error_count,
        'parse_error_paths': parse_error_paths,
        'parse_error_paths_truncated': parse_error_count > len(parse_error_paths),
    }
