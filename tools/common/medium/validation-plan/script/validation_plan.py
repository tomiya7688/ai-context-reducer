#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def classify(path: str) -> list[str]:
    p = path.lower()
    out = []
    if any(x in p for x in ('ui', 'view', 'scene', 'widget', 'layout', '.gd')):
        out += ['headless smoke if possible', 'visual confirmation when acceptance is visual']
    if any(x in p for x in ('package', 'installer', 'publish', 'release', 'dist')):
        out += ['artifact generation', 'artifact smoke']
    if any(x in p for x in ('parser', 'lexer', 'rule', 'validator', 'protocol')):
        out += ['targeted regression tests', 'contract/spec check']
    if any(x in p for x in ('random', 'simulation', 'physics', 'agent')):
        out += ['deterministic seam or fixed seed', 'bounded runtime']
    if Path(p).suffix in {'.json', '.yaml', '.yml', '.toml', '.csv'}:
        out += ['schema/parser validation', 'representative data check']
    if Path(p).suffix in {'.py', '.cs', '.go', '.c', '.h', '.cpp', '.hpp', '.gd'}:
        out += ['targeted tests', 'syntax/build check']
    return list(dict.fromkeys(out)) or ['targeted validation']


def main():
    parser = argparse.ArgumentParser(description='Suggest the smallest sufficient validation for changed files as self-describing JSON.')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()

    result = {
        'tool': 'validation-plan',
        'status': 'ok',
        'validation_by_file': [
            {
                'changed_file': path,
                'recommended_validation': classify(path),
            }
            for path in args.files
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
