from __future__ import annotations

import fnmatch


# match_any はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def match_any(path: str, patterns: list[str]) -> bool:
    normalized = path.replace('\\', '/')
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


# classify はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def classify(path: str, profile: dict[str, object]) -> dict[str, object]:
    layer = None
    role = None
    for item in profile.get('layers', []):
        if match_any(path, item.get('patterns', [])):
            layer = item.get('name')
            break
    for item in profile.get('roles', []):
        if match_any(path, item.get('patterns', [])):
            role = item.get('name')
            break
    boundary = role in set(profile.get('boundary_roles', []))
    return {'path': path, 'layer': layer, 'role': role, 'boundary': boundary}


# route_hint はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def route_hint(item: dict[str, object]) -> str:
    if item['boundary']:
        return 'inspect boundary contract and both sides before broader expansion'
    if item['layer'] and item['role']:
        return f"inspect {item['layer']} {item['role']} and direct collaborators first"
    if item['layer']:
        return f"inspect {item['layer']} scope first"
    return 'unclassified; use generic routing'
