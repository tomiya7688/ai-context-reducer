#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from pathlib import Path

IGNORE = {'.git', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist', '__pycache__', '.godot'}
LANG = {
    '.py': 'python', '.cs': 'csharp', '.go': 'go', '.c': 'c', '.h': 'c',
    '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.hpp': 'cpp', '.hh': 'cpp',
    '.gd': 'gdscript', '.rs': 'rust', '.js': 'javascript', '.ts': 'typescript', '.java': 'java'
}

TYPE_SIGNALS = {
    'game': {'project.godot', 'unityproject', 'game', 'assets', 'scenes'},
    'gui': {'ui', 'views', 'widgets', 'forms', 'mainwindow', 'window'},
    'compiler': {'lexer', 'parser', 'token', 'ast', 'compiler', 'interpreter', 'grammar'},
    'data-tool': {'dataset', 'etl', 'converter', 'export', 'importer', 'migration'},
    'packaged-app': {'installer', 'package', 'publish', 'release', 'dist'},
    'simulation': {'simulation', 'simulator', 'agent', 'physics', 'seed', 'random'},
    'rule-heavy': {'rules', 'specification', 'protocol', 'validator', 'legal', 'policy'},
}


def files(root):
    for p in root.rglob('*'):
        if any(part.lower() in IGNORE for part in p.parts):
            continue
        if p.is_file():
            yield p


def detect_types(paths):
    hay = ' '.join(str(p).lower() for p in paths)
    return [name for name, words in TYPE_SIGNALS.items() if any(word in hay for word in words)]


def recommend(size, languages, project_types, docs, tests, has_git):
    rec = ['common/small/analyze-and-recommend', 'common/small/repo-profile', 'common/small/source-of-truth-candidates']
    cond = ['common/small/doc-index'] if docs else []
    if has_git:
        rec.append('common/medium/compact-diff')
        cond.extend(['common/medium/remote-delta', 'common/medium/change-router', 'common/medium/context-pack-builder'])
    if tests:
        cond.extend(['common/medium/validation-plan', 'common/medium/compact-log'])
    if docs:
        cond.extend(['common/medium/acceptance-extractor', 'common/medium/exploration-stop-check'])
    if size in {'medium', 'large'}:
        rec.append('common/medium/change-router')
        cond.extend(['common/medium/responsibility-candidates', 'common/medium/doc-duplicate-hints', 'common/large/hotspot-report'])
    if size == 'large':
        rec.extend(['common/large/context-manifest', 'common/large/target-slice', 'common/large/context-budget'])
    if 'rule-heavy' in project_types:
        cond.append('common/medium/policy-index')
    for lang, _ in languages[:3]:
        if lang not in {'other', 'rust', 'javascript', 'typescript', 'java'}:
            rec.append(f'{lang}/small')
            if size in {'medium', 'large'}:
                cond.append(f'{lang}/medium')
            if size == 'large':
                cond.append(f'{lang}/large')
    if project_types:
        cond.append('profiles/project-type-profile')
    return sorted(dict.fromkeys(rec)), sorted(dict.fromkeys(cond))


def main():
    ap = argparse.ArgumentParser(description='Low-level tool selector. Prefer analyze-and-recommend for normal adoption.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    paths = list(files(root))
    langs = Counter(LANG.get(p.suffix.lower(), 'other') for p in paths)
    size = 'small' if len(paths) < 200 else 'medium' if len(paths) < 2000 else 'large'
    docs = sum(1 for p in paths if p.suffix.lower() in {'.md', '.rst', '.txt'})
    tests = sum(1 for p in paths if 'test' in p.name.lower() or 'tests' in {x.lower() for x in p.parts})
    types = detect_types(paths)
    rec, cond = recommend(size, langs.most_common(), types, docs, tests, (root / '.git').exists())
    out = {
        'project_size': size,
        'files': len(paths),
        'languages': dict(langs.most_common()),
        'project_types': types,
        'docs': docs,
        'tests': tests,
        'recommended': rec,
        'conditional': cond,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"size={size} files={len(paths)} languages={dict(langs.most_common())}")
        print('types=' + (', '.join(types) if types else 'unknown'))
        print('recommended:')
        for item in rec:
            print(f'  - {item}')
        if cond:
            print('conditional:')
            for item in cond:
                print(f'  - {item}')

if __name__ == '__main__':
    main()
