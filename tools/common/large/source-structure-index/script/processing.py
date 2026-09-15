from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path


def _relpath(raw: str, root: Path | None) -> str:
    path = Path(raw)
    if root is not None and path.is_absolute():
        try:
            path = path.resolve().relative_to(root.resolve())
        except (OSError, ValueError):
            pass
    return path.as_posix()


def _python_module(path: str) -> str | None:
    if not path.endswith('.py'):
        return None
    parts = list(Path(path).with_suffix('').parts)
    if parts and parts[-1] == '__init__':
        parts.pop()
    return '.'.join(parts) if parts else None


def _go_package(module: str, path: str) -> str | None:
    if not module or not path.endswith('.go'):
        return None
    parent = Path(path).parent.as_posix()
    if parent in ('', '.'):
        return module
    return module.rstrip('/') + '/' + parent


def _add_node(nodes: dict[str, dict], node: dict) -> None:
    node_id = node['id']
    current = nodes.get(node_id)
    if current is None:
        nodes[node_id] = node
        return
    for key, value in node.items():
        if key not in current or current[key] in (None, '', []):
            current[key] = value


def _edge_key(edge: dict) -> tuple[str, str, str]:
    return edge['from'], edge['to'], edge['kind']


def build_index(symbol_payloads: list[dict], graph_payloads: list[dict], root: Path | None = None) -> dict:
    nodes: dict[str, dict] = {}
    edges: dict[tuple[str, str, str], dict] = {}
    input_truncated = False
    input_errors: list[str] = []

    for source_name, payload in symbol_payloads:
        if not isinstance(payload, (list, dict)):
            input_errors.append(f'{source_name}: unsupported symbol payload')
            continue
        rows = payload.get('files', []) if isinstance(payload, dict) else payload
        if isinstance(payload, dict) and any(value is True for key, value in payload.items() if key.endswith('truncated')):
            input_truncated = True
        for row in rows:
            if not isinstance(row, dict) or not row.get('file'):
                continue
            path = _relpath(str(row['file']), root)
            file_id = f'file:{path}'
            _add_node(nodes, {'id': file_id, 'kind': 'file', 'path': path})

            module_name = _python_module(path)
            if module_name:
                module_id = f'module:{module_name}'
                _add_node(nodes, {'id': module_id, 'kind': 'module', 'name': module_name})
                edge = {'from': module_id, 'to': file_id, 'kind': 'contains_file'}
                edges[_edge_key(edge)] = edge

            for symbol in row.get('symbols', []):
                if not isinstance(symbol, dict) or not symbol.get('name'):
                    continue
                name = str(symbol['name'])
                qualified_name = str(symbol.get('qualified_name') or f'{path}::{name}')
                symbol_id = f'symbol:{qualified_name}'
                node = {
                    'id': symbol_id,
                    'kind': 'symbol',
                    'name': name,
                    'qualified_name': qualified_name,
                    'path': path,
                    'symbol_kind': str(symbol.get('kind', 'unknown')),
                }
                if isinstance(symbol.get('line'), int):
                    node['line'] = symbol['line']
                if isinstance(symbol.get('end_line'), int):
                    node['end_line'] = symbol['end_line']
                _add_node(nodes, node)
                edge = {'from': file_id, 'to': symbol_id, 'kind': 'owns'}
                edges[_edge_key(edge)] = edge

    for source_name, payload in graph_payloads:
        if not isinstance(payload, dict):
            input_errors.append(f'{source_name}: unsupported graph payload')
            continue
        if any(value is True for key, value in payload.items() if key.endswith('truncated')):
            input_truncated = True

        for node in payload.get('nodes', []):
            if isinstance(node, dict) and node.get('id') and node.get('kind'):
                _add_node(nodes, dict(node))

        go_module = str(payload.get('module') or '')
        if go_module:
            for node in list(nodes.values()):
                if node.get('kind') != 'file' or not node.get('path'):
                    continue
                package_name = _go_package(go_module, str(node['path']))
                if not package_name:
                    continue
                package_id = f'module:{package_name}'
                _add_node(nodes, {'id': package_id, 'kind': 'module', 'name': package_name})
                edge = {'from': package_id, 'to': node['id'], 'kind': 'contains_file'}
                edges[_edge_key(edge)] = edge

        for raw_edge in payload.get('edges', []):
            if not isinstance(raw_edge, dict) or not raw_edge.get('from') or not raw_edge.get('to'):
                continue
            source = str(raw_edge['from'])
            target = str(raw_edge['to'])
            kind = str(raw_edge.get('kind') or 'depends_on')

            if payload.get('nodes'):
                source_id, target_id = source, target
            else:
                source_id, target_id = f'module:{source}', f'module:{target}'
                _add_node(nodes, {'id': source_id, 'kind': 'module', 'name': source})
                _add_node(nodes, {'id': target_id, 'kind': 'module', 'name': target})

            edge = {'from': source_id, 'to': target_id, 'kind': kind}
            edges[_edge_key(edge)] = edge

    return {
        'format': 'acr-source-structure-index-v1',
        'nodes': sorted(nodes.values(), key=lambda row: row['id']),
        'edges': sorted(edges.values(), key=lambda row: (row['from'], row['to'], row['kind'])),
        'input_truncated': input_truncated,
        'input_errors': input_errors,
    }


def query_nodes(index: dict, pattern: str, max_results: int) -> tuple[list[dict], bool]:
    needle = pattern.casefold()
    ranked: list[tuple[int, str, dict]] = []
    for node in index.get('nodes', []):
        values = [
            str(node.get('id', '')),
            str(node.get('qualified_name', '')),
            str(node.get('name', '')),
            str(node.get('path', '')),
        ]
        folded = [value.casefold() for value in values if value]
        if not any(needle in value for value in folded):
            continue
        exact = any(needle == value for value in folded)
        prefix = any(value.startswith(needle) for value in folded)
        rank = 0 if exact else 1 if prefix else 2
        ranked.append((rank, str(node.get('id', '')), node))
    ranked.sort(key=lambda row: (row[0], row[1]))
    rows = [row[2] for row in ranked]
    if max_results > 0:
        return rows[:max_results], len(rows) > max_results
    return rows, False


def resolve_target(index: dict, target: str) -> tuple[str, list[dict]]:
    matches, _ = query_nodes(index, target, 0)
    exact = []
    needle = target.casefold()
    for node in matches:
        values = {
            str(node.get('id', '')).casefold(),
            str(node.get('qualified_name', '')).casefold(),
            str(node.get('name', '')).casefold(),
            str(node.get('path', '')).casefold(),
        }
        if needle in values:
            exact.append(node)
    if len(exact) == 1:
        return 'ok', exact
    if len(exact) > 1:
        return 'target_ambiguous', exact
    if len(matches) == 1:
        return 'ok', matches
    if matches:
        return 'target_ambiguous', matches
    return 'target_not_found', []


def _cycle_groups(node_ids: set[str], edges: list[dict]) -> list[list[str]]:
    graph: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if edge['from'] in node_ids and edge['to'] in node_ids:
            graph[edge['from']].append(edge['to'])

    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    groups: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for target in graph.get(node, []):
            if target not in indices:
                strongconnect(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])

        if lowlinks[node] == indices[node]:
            component = []
            while True:
                current = stack.pop()
                on_stack.remove(current)
                component.append(current)
                if current == node:
                    break
            if len(component) > 1 or node in graph.get(node, []):
                groups.append(sorted(component))

    for node in sorted(node_ids):
        if node not in indices:
            strongconnect(node)
    return sorted(groups)


def expand(index: dict, start_id: str, depth: int, max_nodes: int, direction: str) -> dict:
    nodes_by_id = {node['id']: node for node in index.get('nodes', []) if node.get('id')}
    outgoing: dict[str, list[dict]] = defaultdict(list)
    incoming: dict[str, list[dict]] = defaultdict(list)
    for edge in index.get('edges', []):
        outgoing[edge['from']].append(edge)
        incoming[edge['to']].append(edge)

    visited = {start_id}
    levels = {start_id: 0}
    queue = deque([start_id])
    truncated = False

    while queue:
        current = queue.popleft()
        current_depth = levels[current]
        if current_depth >= depth:
            continue
        candidates = []
        if direction in ('out', 'both'):
            candidates.extend(edge['to'] for edge in outgoing.get(current, []))
        if direction in ('in', 'both'):
            candidates.extend(edge['from'] for edge in incoming.get(current, []))
        for target in sorted(set(candidates)):
            if target in visited:
                continue
            if max_nodes > 0 and len(visited) >= max_nodes:
                truncated = True
                continue
            visited.add(target)
            levels[target] = current_depth + 1
            queue.append(target)

    selected_edges = [
        edge for edge in index.get('edges', [])
        if edge['from'] in visited and edge['to'] in visited
    ]
    selected_nodes = []
    for node_id in sorted(visited, key=lambda value: (levels.get(value, 0), value)):
        node = dict(nodes_by_id.get(node_id, {'id': node_id, 'kind': 'unknown'}))
        node['distance'] = levels.get(node_id, 0)
        node['fan_out'] = len(outgoing.get(node_id, []))
        node['fan_in'] = len(incoming.get(node_id, []))
        selected_nodes.append(node)

    return {
        'start_node_id': start_id,
        'depth': depth,
        'direction': direction,
        'nodes': selected_nodes,
        'edges': selected_edges,
        'nodes_truncated': truncated,
        'cycle_groups': _cycle_groups(visited, selected_edges),
    }
