#!/usr/bin/env python3
import argparse
import fnmatch
import json
import subprocess
from pathlib import Path

TOOL = 'affected-tests'


def git_changed(root, base):
    cmd = ['git', '-C', root, 'diff', '--name-only']
    if base:
        cmd.append(base)
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or 'git diff failed')
    return [line.strip().replace('\\', '/') for line in completed.stdout.splitlines() if line.strip()]


def load_json(path):
    if not path:
        return {}
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def defaults_for(path):
    normalized = path.replace('\\', '/')
    stem = Path(normalized).stem
    out = []
    if normalized.startswith('src/'):
        rel = normalized[4:]
        out += [f'tests/{rel}', f'tests/test_{stem}.py']
    if '/src/' in normalized:
        prefix, rel = normalized.split('/src/', 1)
        out += [f'{prefix}/tests/{rel}', f'{prefix}/tests/test_{stem}.py']
    return out


def uniq(items):
    seen, out = set(), []
    for item in items:
        item = item.replace('\\', '/')
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def dependency_consumers(changed, dependency_map):
    needles = []
    for path in changed:
        normalized = path.replace('\\', '/')
        no_ext = str(Path(normalized).with_suffix('')).replace('\\', '/')
        stem = Path(no_ext).name
        parent = str(Path(no_ext).parent).replace('\\', '/')
        needles += [no_ext, no_ext.replace('/', '.'), stem]
        if parent not in ('', '.'):
            needles += [parent, parent.replace('/', '.')]
    needles = uniq(needles)
    consumers = []
    for row in dependency_map.get('files', []):
        if not isinstance(row, dict):
            continue
        for imp in row.get('imports', []):
            for needle in needles:
                if needle and (imp == needle or imp.endswith('/' + needle) or imp.endswith('.' + needle)):
                    consumers.append(str(row.get('file', '')).replace('\\', '/'))
                    break
    return uniq(consumers)


def dependency_state(dependency_map, used):
    if not used:
        return {'used': False}
    reasons = []
    if dependency_map.get('scan_truncated') or dependency_map.get('truncated'):
        reasons.append('dependency_map_truncated')
    for key in ('parse_error_count', 'read_error_count', 'walk_error_count'):
        count = dependency_map.get(key, 0)
        if isinstance(count, int) and count > 0:
            reasons.append(f'{key}={count}')
    return {'used': True, 'complete': not reasons, 'reasons': reasons}


def analyze(changed, cfg, dependency_map=None, dependency_map_used=False):
    dependency_map = dependency_map or {}
    mappings = cfg.get('mappings', [])
    broad = cfg.get('broader_patterns', [
        '**/core/**', '**/shared/**', '**/schema.*', '**/api/**',
        'go.mod', 'go.sum', 'pyproject.toml', 'package.json',
    ])
    tests, reasons = [], []
    matched_explicit = False
    broader = False
    for path in changed:
        for mapping in mappings:
            if fnmatch.fnmatch(path, mapping.get('source', '')):
                matched_explicit = True
                tests += mapping.get('tests', [])
                if mapping.get('broader'):
                    broader = True
                    reasons.append(f'broader mapping: {path}')
        tests += defaults_for(path)
        if any(fnmatch.fnmatch(path, pattern) for pattern in broad):
            broader = True
            reasons.append(f'broad-impact pattern: {path}')

    consumers = dependency_consumers(changed, dependency_map)
    for consumer in consumers:
        tests += defaults_for(consumer)
    if consumers:
        reasons.append(f'dependency-map consumers: {len(consumers)}')

    tests = uniq(tests)
    if not changed:
        confidence = 'low'
        reasons.append('no changed files')
    elif broader:
        confidence = 'medium'
    elif matched_explicit:
        confidence = 'high'
    elif tests:
        confidence = 'medium'
    else:
        confidence = 'low'
        reasons.append('no mapping or naming candidate')

    dep_state = dependency_state(dependency_map, dependency_map_used)
    impact_uncertain = bool(dep_state.get('used') and not dep_state.get('complete'))
    if impact_uncertain:
        reasons += dep_state['reasons']
        if confidence == 'high':
            confidence = 'medium'
        fallback = 'broader-or-full'
    elif broader:
        fallback = 'broader'
    elif confidence == 'low':
        fallback = 'subsystem-or-full'
    else:
        fallback = 'none'

    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if impact_uncertain else 'ok',
        'changed_files': uniq(changed),
        'test_candidates': tests,
        'confidence': confidence,
        'fallback': fallback,
        'impact_uncertain': impact_uncertain,
        'dependency_map': dep_state,
        'reasons': uniq(reasons),
    }


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Lightweight affected-test selector')
    parser.add_argument('--root', default='.')
    parser.add_argument('--base', help='git diff base, e.g. origin/main...HEAD')
    parser.add_argument('--changed', nargs='*', help='explicit changed files; bypass git')
    parser.add_argument('--config', help='JSON config')
    parser.add_argument('--dependency-map', help='optional import/dependency map JSON')
    parser.add_argument('--json', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()

    try:
        changed = [item.replace('\\', '/') for item in args.changed] if args.changed is not None else git_changed(args.root, args.base)
    except Exception as exc:
        emit({'tool': TOOL, 'status': 'git_query_failed', 'error': str(exc)})
        return 2
    try:
        cfg = load_json(args.config)
    except Exception as exc:
        emit({'tool': TOOL, 'status': 'config_read_failed', 'error': str(exc)})
        return 2
    try:
        dependency_map = load_json(args.dependency_map)
    except Exception as exc:
        emit({'tool': TOOL, 'status': 'dependency_map_read_failed', 'error': str(exc)})
        return 2

    emit(analyze(changed, cfg, dependency_map, bool(args.dependency_map)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
