#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path

IGNORE = {'.git','.venv','venv','node_modules','bin','obj','build','dist','__pycache__','.godot','.cache'}
LANG = {'.py':'python','.cs':'csharp','.go':'go','.c':'c','.h':'c','.cpp':'cpp','.cc':'cpp','.cxx':'cpp','.hpp':'cpp','.hh':'cpp','.gd':'gdscript'}
TYPE_SIGNALS = {
    'game': {'project.godot','assets','scenes','game'},
    'gui': {'ui','views','widgets','forms','window'},
    'compiler': {'lexer','parser','token','ast','compiler','grammar'},
    'data-tool': {'dataset','etl','converter','export','importer','migration'},
    'packaged-app': {'installer','package','publish','release','dist'},
    'simulation': {'simulation','simulator','agent','physics','seed','random'},
    'rule-heavy': {'rules','specification','protocol','validator','policy'},
}
EXTERNAL = ['rg','fd','ast-grep','sg','ctags','tree-sitter','scc','git-sizer','semgrep']


def walk(root):
    for p in root.rglob('*'):
        if any(part.lower() in IGNORE for part in p.parts):
            continue
        if p.is_file():
            yield p


def git(root, *args):
    try:
        return subprocess.check_output(['git','-C',str(root),*args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ''


def main():
    ap = argparse.ArgumentParser(description='Analyze a repo and recommend ai-context-reducer techniques/tools.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    paths = list(walk(root))
    langs = Counter(LANG.get(p.suffix.lower(),'other') for p in paths)
    size = 'small' if len(paths) < 200 else 'medium' if len(paths) < 2000 else 'large'
    hay = ' '.join(str(p.relative_to(root)).lower() for p in paths)
    types = [k for k, words in TYPE_SIGNALS.items() if any(w in hay for w in words)]
    docs = [p for p in paths if p.suffix.lower() in {'.md','.rst','.txt'}]
    tests = [p for p in paths if 'test' in p.name.lower() or any(x.lower() in {'test','tests'} for x in p.parts)]
    large_files = sum(1 for p in paths if p.stat().st_size >= 100_000)
    has_git = (root / '.git').exists()
    dirty = bool(git(root,'status','--porcelain')) if has_git else False
    external = [x for x in EXTERNAL if shutil.which(x)]

    techniques = ['AI_CONTEXT minimum core','Search-first / Read-second','Exploration stop condition','Source of Truth','Targeted validation']
    tools = ['common/small/doc-index','common/small/file-role-map']
    if has_git:
        techniques += ['Diff-first workflow','Remote Delta First']
        tools += ['common/medium/compact-diff','common/medium/remote-delta','common/medium/change-router']
    if docs:
        techniques.append('Document routing / heading-first reading')
    if len(paths) >= 200:
        techniques += ['Responsibility Map','Change Routing Map']
        tools += ['common/medium/responsibility-candidates','common/medium/context-pack-builder']
    if len(paths) >= 2000 or large_files:
        techniques += ['Source Structure Index','Bounded excerpts','Context manifest']
        tools += ['common/large/context-manifest','common/large/hotspot-report','common/large/target-slice','common/large/context-budget']
    if tests:
        techniques.append('Validation Routing')
        tools.append('common/medium/validation-plan')
    if 'rule-heavy' in types:
        techniques += ['Policy Routing','Compact checker output']
        tools.append('common/medium/policy-index')
    if {'game','gui'} & set(types):
        techniques.append('Headless-first + visual confirmation when required')
    if 'simulation' in types:
        techniques.append('Deterministic seam / structured observation')
    if 'packaged-app' in types:
        techniques.append('Artifact-boundary validation')
    for lang, _ in langs.most_common(3):
        if lang in {'python','csharp','go','c','cpp','gdscript'}:
            tools.append(f'{lang}/small')
            if size in {'medium','large'}:
                tools.append(f'{lang}/medium')
            if size == 'large':
                tools.append(f'{lang}/large')

    out = {
        'project': root.name, 'size': size, 'files': len(paths), 'docs': len(docs), 'tests': len(tests),
        'large_files_100kb_plus': large_files, 'languages': dict(langs.most_common()), 'project_types': types,
        'git': {'available': has_git, 'dirty': dirty}, 'external_tools_available': external,
        'recommended_techniques': list(dict.fromkeys(techniques)),
        'recommended_tools': list(dict.fromkeys(tools)),
        'next_step': 'Create/update a minimal AI_CONTEXT.md, then run only the recommended tools needed for the current task.'
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"project={out['project']} size={size} files={len(paths)} docs={len(docs)} tests={len(tests)}")
        print('languages=' + ', '.join(f'{k}:{v}' for k,v in langs.most_common()))
        print('types=' + (', '.join(types) if types else 'unknown'))
        print('external=' + (', '.join(external) if external else 'none detected'))
        print('\nrecommended techniques:')
        for x in out['recommended_techniques']: print('  - ' + x)
        print('\nrecommended tools:')
        for x in out['recommended_tools']: print('  - ' + x)
        print('\nnext: ' + out['next_step'])

if __name__ == '__main__':
    main()
