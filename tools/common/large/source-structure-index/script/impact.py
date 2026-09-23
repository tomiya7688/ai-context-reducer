from __future__ import annotations

from collections import defaultdict, deque


# platform差を吸収したpath keyへ正規化し、依存edgeの照合漏れを避ける。
def _path_key(raw: str) -> str:
    value = str(raw).replace('\\', '/')
    while value.startswith('./'):
        value = value[2:]
    return value


# 変更nodeから逆依存を辿り、完全性signal付きのbounded impact scopeを作る。
def affected_scope(index: dict, changed_files: list[str], max_results: int) -> dict:
    nodes_by_id = {
        str(node['id']): node
        for node in index.get('nodes', [])
        if isinstance(node, dict) and node.get('id')
    }
    file_ids_by_path = {
        _path_key(str(node.get('path', ''))): node_id
        for node_id, node in nodes_by_id.items()
        if node.get('kind') == 'file' and node.get('path')
    }

    file_owners: dict[str, set[str]] = defaultdict(set)
    reverse_dependencies: dict[str, set[str]] = defaultdict(set)
    dependency_edge_count = 0
    for edge in index.get('edges', []):
        if not isinstance(edge, dict):
            continue
        source = str(edge.get('from', ''))
        target = str(edge.get('to', ''))
        kind = str(edge.get('kind', ''))
        if not source or not target:
            continue
        if kind == 'contains_file' and nodes_by_id.get(source, {}).get('kind') == 'module':
            file_owners[target].add(source)
        elif kind == 'depends_on':
            reverse_dependencies[target].add(source)
            dependency_edge_count += 1

    matched = []
    unmatched = []
    ownerless = []
    seed_modules: set[str] = set()
    seen_changed = set()
    for raw_path in changed_files:
        path = _path_key(raw_path)
        if path in seen_changed:
            continue
        seen_changed.add(path)
        file_id = file_ids_by_path.get(path)
        if not file_id:
            unmatched.append(path)
            continue
        owners = sorted(file_owners.get(file_id, set()))
        matched.append({
            'path': path,
            'file_node_id': file_id,
            'seed_module_ids': owners,
        })
        if not owners:
            ownerless.append(path)
        seed_modules.update(owners)

    distance: dict[str, int] = {module_id: 0 for module_id in seed_modules}
    queue = deque(sorted(seed_modules))
    while queue:
        current = queue.popleft()
        next_distance = distance[current] + 1
        for dependent in sorted(reverse_dependencies.get(current, set())):
            previous = distance.get(dependent)
            if previous is not None and previous <= next_distance:
                continue
            distance[dependent] = next_distance
            queue.append(dependent)

    affected = []
    for module_id, module_distance in distance.items():
        node = dict(nodes_by_id.get(module_id, {'id': module_id, 'kind': 'module'}))
        node['distance_from_change'] = module_distance
        affected.append(node)
    affected.sort(key=lambda row: (row['distance_from_change'], str(row.get('id', ''))))

    affected_total = len(affected)
    truncated = max_results > 0 and affected_total > max_results
    returned = affected[:max_results] if max_results > 0 else affected

    uncertainty_reasons = []
    if bool(index.get('input_truncated')):
        uncertainty_reasons.append('source_structure_index_input_was_truncated')
    if unmatched:
        uncertainty_reasons.append('some_changed_files_are_not_present_in_the_index')
    if ownerless:
        uncertainty_reasons.append('some_changed_files_have_no_module_owner_in_the_index')
    if seed_modules and dependency_edge_count == 0:
        uncertainty_reasons.append('dependency_relationships_are_absent_or_empty')
    if truncated:
        uncertainty_reasons.append('affected_module_output_was_truncated')

    impact_uncertain = bool(uncertainty_reasons)
    return {
        'changed_files': sorted(seen_changed),
        'matched_changed_files': matched,
        'unmatched_changed_files': unmatched,
        'changed_files_without_module_owner': ownerless,
        'seed_module_ids': sorted(seed_modules),
        'dependency_edge_count': dependency_edge_count,
        'affected_module_count_total': affected_total,
        'affected_modules_returned': len(returned),
        'affected_modules_truncated': truncated,
        'affected_modules': returned,
        'impact_uncertain': impact_uncertain,
        'uncertainty_reasons': uncertainty_reasons,
        'recommended_validation_scope': 'broader_or_full' if impact_uncertain else 'targeted_dependents',
    }
