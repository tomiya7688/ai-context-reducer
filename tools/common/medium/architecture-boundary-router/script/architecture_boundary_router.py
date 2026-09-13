#!/usr/bin/env python3
import argparse
import json

from commander import route_paths


def main():
    parser = argparse.ArgumentParser(description='Classify changed paths using an architecture routing profile.')
    parser.add_argument('--profile', required=True)
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    result = route_paths(args.profile, args.paths)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    for row in result['routes']:
        print(row['path'])
        print(f"  layer={row['layer'] or '-'} role={row['role'] or '-'} boundary={'yes' if row['boundary'] else 'no'}")
        print('  route=' + row['route_hint'])


if __name__ == '__main__':
    main()
