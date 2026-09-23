from __future__ import annotations

from collections import defaultdict

SIGNATURE_LIMIT = 200


# 外部tool由来の値をboundedに保ち、index metadataがcontextを占有しないようにする。
def _bounded(value: object, limit: int = SIGNATURE_LIMIT) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if len(text) <= limit else text[:limit]


# scopeとsymbol名を安定したqualified nameへ統合し、ownership routingに使える形にする。
def _qualified(path: str, scope: str | None, name: str) -> str:
    if scope:
        return f'{path}::{scope}::{name}'
    return f'{path}::{name}'


# ctags固有JSONを共通symbol schemaへ正規化し、後段をbackend非依存にする。
def normalize_ctags_rows(rows: object) -> tuple[dict[str, object], dict[str, object]]:
    if not isinstance(rows, list):
        raise ValueError('ctags JSON input must be a list of JSON tag rows')

    by_file: dict[str, list[dict[str, object]]] = defaultdict(list)
    tag_count = 0
    skipped_rows = 0
    languages: set[str] = set()

    for row in rows:
        if not isinstance(row, dict):
            skipped_rows += 1
            continue
        row_type = row.get('_type')
        if row_type not in (None, 'tag'):
            continue
        name = row.get('name')
        path = row.get('path') or row.get('input')
        if not name or not path:
            skipped_rows += 1
            continue

        path_text = str(path)
        name_text = str(name)
        scope = str(row.get('scope')) if row.get('scope') else None
        symbol = {
            'name': name_text,
            'qualified_name': _qualified(path_text, scope, name_text),
            'kind': str(row.get('kind') or 'unknown'),
        }
        line = row.get('line')
        end_line = row.get('end')
        if isinstance(line, int):
            symbol['line'] = line
        if isinstance(end_line, int):
            symbol['end_line'] = end_line
        language = _bounded(row.get('language'))
        if language:
            symbol['language'] = language
            languages.add(language)
        signature = _bounded(row.get('signature'))
        if signature:
            symbol['signature'] = signature
        if scope:
            symbol['owner_qualified_name'] = f'{path_text}::{scope}'
        by_file[path_text].append(symbol)
        tag_count += 1

    files = [
        {
            'file': path,
            'symbols': sorted(symbols, key=lambda item: (int(item.get('line', 0)), str(item['qualified_name']))),
        }
        for path, symbols in sorted(by_file.items())
    ]
    return (
        {
            'files': files,
            'input_adapter': 'universal-ctags-json',
            'truncated': False,
        },
        {
            'tag_count': tag_count,
            'file_count': len(files),
            'skipped_row_count': skipped_rows,
            'languages': sorted(languages),
        },
    )
