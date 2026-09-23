from __future__ import annotations


# SCIP object/dictの差を吸収してfieldを安全に取得し、adapter外へ形式差を漏らさない。
def _field(row: dict, camel: str, snake: str, default=None):
    return row[camel] if camel in row else row.get(snake, default)


# SCIP rangeから必要な行範囲だけを取り出し、欠損値は無理に補完しない。
def _range_lines(raw: object) -> tuple[int | None, int | None]:
    if not isinstance(raw, list) or len(raw) not in (3, 4):
        return None, None
    try:
        start = int(raw[0]) + 1
        end = int(raw[2]) + 1 if len(raw) == 4 else start
    except (TypeError, ValueError):
        return None, None
    return start, end


# SCIP role bitmaskを人が読めるbounded labelへ変換する。
def _roles(occurrence: dict) -> int:
    raw = _field(occurrence, 'symbolRoles', 'symbol_roles', 0)
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


# SCIP signatureをbounded文字列へ縮め、詳細情報によるcontext肥大を防ぐ。
def _signature(symbol: dict) -> str | None:
    payload = _field(symbol, 'signatureDocumentation', 'signature_documentation')
    if not isinstance(payload, dict) or not payload.get('text'):
        return None
    return str(payload['text'])


# SCIP print JSONを共通symbol/dependency schemaへ正規化し、backend依存を隔離する。
def normalize_scip_print(payload: object) -> tuple[list[dict], dict, dict]:
    if not isinstance(payload, dict):
        raise ValueError('SCIP print JSON must be an object')
    documents = payload.get('documents')
    if not isinstance(documents, list):
        raise ValueError('SCIP print JSON is missing documents[]')

    definitions: dict[str, tuple[int | None, int | None]] = {}
    symbol_documents: dict[str, str] = {}
    rows: list[tuple[str, dict]] = []

    for document in documents:
        if not isinstance(document, dict):
            continue
        path = _field(document, 'relativePath', 'relative_path')
        if not path:
            continue
        path = str(path).replace('\\', '/')
        rows.append((path, document))
        for symbol in document.get('symbols', []):
            if isinstance(symbol, dict) and symbol.get('symbol'):
                symbol_documents[str(symbol['symbol'])] = path
        for occurrence in document.get('occurrences', []):
            if isinstance(occurrence, dict) and occurrence.get('symbol') and (_roles(occurrence) & 0x1):
                definitions.setdefault(str(occurrence['symbol']), _range_lines(occurrence.get('range')))

    symbol_payload: list[dict] = []
    nodes: dict[str, dict] = {}
    edges: dict[tuple[str, str, str], dict] = {}

    for path, document in rows:
        language = str(document.get('language') or '')
        file_id = f'file:{path}'
        module_id = f'module:scip:{path}'
        nodes[module_id] = {'id': module_id, 'kind': 'module', 'name': path, 'source_kind': 'scip_document'}
        edges[(module_id, file_id, 'contains_file')] = {'from': module_id, 'to': file_id, 'kind': 'contains_file'}

        symbols = []
        for symbol in document.get('symbols', []):
            if not isinstance(symbol, dict) or not symbol.get('symbol'):
                continue
            qualified = str(symbol['symbol'])
            item = {
                'name': str(_field(symbol, 'displayName', 'display_name') or qualified),
                'qualified_name': qualified,
                'kind': str(symbol.get('kind', 'unknown')),
            }
            if language:
                item['language'] = language
            owner = _field(symbol, 'enclosingSymbol', 'enclosing_symbol')
            if owner:
                item['owner_qualified_name'] = str(owner)
            signature = _signature(symbol)
            if signature:
                item['signature'] = signature
            line, end_line = definitions.get(qualified, (None, None))
            if line is not None:
                item['line'] = line
            if end_line is not None:
                item['end_line'] = end_line
            symbols.append(item)

            for relationship in symbol.get('relationships', []):
                if not isinstance(relationship, dict) or not relationship.get('symbol'):
                    continue
                target_path = symbol_documents.get(str(relationship['symbol']))
                if target_path and target_path != path:
                    target = f'module:scip:{target_path}'
                    edges[(module_id, target, 'depends_on')] = {'from': module_id, 'to': target, 'kind': 'depends_on'}

        symbol_payload.append({'file': path, 'symbols': symbols})

        for occurrence in document.get('occurrences', []):
            if not isinstance(occurrence, dict) or not occurrence.get('symbol') or (_roles(occurrence) & 0x1):
                continue
            target_path = symbol_documents.get(str(occurrence['symbol']))
            if target_path and target_path != path:
                target = f'module:scip:{target_path}'
                edges[(module_id, target, 'depends_on')] = {'from': module_id, 'to': target, 'kind': 'depends_on'}

    metadata = payload.get('metadata') if isinstance(payload.get('metadata'), dict) else {}
    tool_info = _field(metadata, 'toolInfo', 'tool_info', {}) if isinstance(metadata, dict) else {}
    adapter_metadata = {
        'source_format': 'scip-print-json',
        'project_root': _field(metadata, 'projectRoot', 'project_root') if isinstance(metadata, dict) else None,
        'indexer': tool_info if isinstance(tool_info, dict) else {},
        'document_count': len(rows),
        'defined_symbol_count': len(symbol_documents),
    }
    graph_payload = {
        'nodes': sorted(nodes.values(), key=lambda row: row['id']),
        'edges': sorted(edges.values(), key=lambda row: (row['from'], row['to'], row['kind'])),
        'truncated': False,
        'source_format': 'scip-print-json',
    }
    return symbol_payload, graph_payload, adapter_metadata
