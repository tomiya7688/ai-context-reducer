#!/usr/bin/env python3
import argparse
import json

from commander import route_paths

TOOL = 'architecture-boundary-router'


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    parser = argparse.ArgumentParser(description='Classify changed paths using an architecture routing profile.')
    parser.add_argument('--profile', required=True)
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--json', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()

    try:
        result = route_paths(args.profile, args.paths)
    except FileNotFoundError as exc:
        print(json.dumps({
            'tool': TOOL,
            'status': 'profile_missing',
            'profile_path': args.profile,
            'error': str(exc),
        }, ensure_ascii=False, indent=2))
        return 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({
            'tool': TOOL,
            'status': 'profile_read_failed',
            'profile_path': args.profile,
            'error': str(exc),
        }, ensure_ascii=False, indent=2))
        return 2

    routes = result.get('routes', [])
    print(json.dumps({
        'tool': TOOL,
        'status': 'ok',
        'profile': result.get('profile'),
        'route_count': len(routes),
        'routes': routes,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
