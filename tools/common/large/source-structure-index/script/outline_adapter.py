from __future__ import annotations

SIGNATURE_LIMIT = 200


# outline由来のsignatureをboundedにし、symbol情報がcontext budgetを圧迫しないようにする。
def _bounded(value: object, limit: int = SIGNATURE_LIMIT) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if len(text) <= limit else text[:limit]


# outline payloadの最小shapeだけを判定し、未知形式を無理に解釈しない。
def _looks_like_outline_file(row: object) -> bool:
    return isinstance(row, dict) and bool(row.get('path')) and isinstance(row.get('items'), list)


# ast-grep outlineとして扱えるpayloadかをcheapに判定する。
def is_ast_grep_outline(payload: object) -> bool:
    if _looks_like_outline_file(payload):
        return True
    if isinstance(payload, list) and payload:
        return all(_looks_like_outline_file(row) for row in payload)
    return False


# nested outlineをownership関係を保った共通symbol列へ平坦化する。
def _flatten_items(path: str, language: str | None, items: list[dict], parents: tuple[str, ...] = ()) -> list[dict]:
    rows = []
    for item in items:
        if not isinstance(item, dict) or not item.get('name'):
            continue
        name = str(item['name'])
        chain = (*parents, name)
        qualified_name = f"{path}::{'::'.join(chain)}"
        item_range = item.get('range') or {}
        start = item_range.get('start') or {}
        end = item_range.get('end') or {}
        row = {
            'name': name,
            'qualified_name': qualified_name,
            'kind': str(item.get('symbolType') or item.get('astKind') or 'unknown'),
        }
        if isinstance(start.get('line'), int):
            row['line'] = start['line'] + 1
        if isinstance(end.get('line'), int):
            row['end_line'] = end['line'] + 1
        if language:
            row['language'] = language
        signature = _bounded(item.get('signature'))
        if signature:
            row['signature'] = signature
        if parents:
            row['owner_qualified_name'] = f"{path}::{'::'.join(parents)}"
        rows.append(row)
        members = item.get('members') or []
        if isinstance(members, list):
            rows.extend(_flatten_items(path, language, members, chain))
    return rows


# 既存共通schemaを保ちつつoutline形式だけを安全に正規化する。
def normalize_symbol_payload(payload: object) -> object:
    if not is_ast_grep_outline(payload):
        return payload
    files = payload if isinstance(payload, list) else [payload]
    rows = []
    for file_row in files:
        path = str(file_row['path'])
        language = str(file_row.get('language')) if file_row.get('language') else None
        rows.append({
            'file': path,
            'symbols': _flatten_items(path, language, file_row.get('items') or []),
        })
    return {
        'files': rows,
        'input_adapter': 'ast-grep-outline',
        'truncated': False,
    }
