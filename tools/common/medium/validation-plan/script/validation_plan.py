#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

VISUAL_TERMS = {'ui', 'view', 'scene', 'widget', 'layout'}
ARTIFACT_TERMS = {'package', 'installer', 'publish', 'release', 'dist'}
CONTRACT_TERMS = {'parser', 'lexer', 'rule', 'rules', 'validator', 'protocol'}
RUNTIME_TERMS = {'random', 'simulation', 'physics', 'agent'}
DATA_EXTS = {'.json', '.yaml', '.yml', '.toml', '.csv'}
SOURCE_EXTS = {'.py', '.cs', '.go', '.c', '.h', '.cpp', '.hpp', '.gd'}


def path_terms(path: str) -> set[str]:
    return {part for part in re.split(r'[^a-z0-9]+', path.lower()) if part}


def classify(path: str) -> list[str]:
    lowered = path.lower()
    terms = path_terms(lowered)
    suffix = Path(lowered).suffix
    out = []
    if terms & VISUAL_TERMS or suffix == '.gd':
        out += ['headless smoke if possible', 'visual confirmation when acceptance is visual']
    if terms & ARTIFACT_TERMS:
        out += ['artifact generation', 'artifact smoke']
    if terms & CONTRACT_TERMS:
        out += ['targeted regression tests', 'contract/spec check']
    if terms & RUNTIME_TERMS:
        out += ['deterministic seam or fixed seed', 'bounded runtime']
    if suffix in DATA_EXTS:
        out += ['schema/parser validation', 'representative data check']
    if suffix in SOURCE_EXTS:
        out += ['targeted tests', 'syntax/build check']
    return list(dict.fromkeys(out)) or ['targeted validation']


def main() -> None:
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
