from __future__ import annotations

from messenger import load_profile
from processing import classify, route_hint


def route_paths(profile_path: str, paths: list[str]) -> dict[str, object]:
    profile = load_profile(profile_path)
    routes = []
    for path in paths:
        row = classify(path, profile)
        row['route_hint'] = route_hint(row)
        routes.append(row)
    return {'profile': profile.get('name'), 'routes': routes}
