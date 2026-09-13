#!/usr/bin/env python3
import argparse
import fnmatch
import json


def load_json(path):
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def match_any(path, patterns):
    path = path.replace('\\', '/')
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def classify(path, profile):
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


def hint(item):
    if item['boundary']:
        return 'inspect boundary contract and both sides before broader expansion'
    if item['layer'] and item['role']:
        return f"inspect {item['layer']} {item['role']} and direct collaborators first"
    if item['layer']:
        return f"inspect {item['layer']} scope first"
    return 'unclassified; use generic routing'


def main():
    parser = argparse.ArgumentParser(description='Classify changed paths using an architecture routing profile.')
    parser.add_argument('--profile', required=True)
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    profile = load_json(args.profile)
    rows = []
    for path in args.paths:
        row = classify(path, profile)
        row['route_hint'] = hint(row)
        rows.append(row)

    if args.json:
        print(json.dumps({'profile': profile.get('name'), 'routes': rows}, ensure_ascii=False, indent=2))
        return

    for row in rows:
        print(row['path'])
        print(f"  layer={row['layer'] or '-'} role={row['role'] or '-'} boundary={'yes' if row['boundary'] else 'no'}")
        print('  route=' + row['route_hint'])


if __name__ == '__main__':
    main()
