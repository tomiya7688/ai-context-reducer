#!/usr/bin/env python3
import argparse
import json
import platform
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


def git_result(root, *args):
    try:
        result = subprocess.run(['git','-C',str(root),*args], text=True, capture_output=True, check=False)
    except OSError:
        return False, ''
    return result.returncode == 0, result.stdout.strip()


def implementation_plan(repo_root):
    system = platform.system().lower()
    arch = platform.machine().lower()
    native_name = 'acr-toolbox.exe' if system == 'windows' else 'acr-toolbox'
    candidates = [
        repo_root / 'tools' / 'bin' / native_name,
        Path(__file__).resolve().parents[4] / 'bin' / native_name,
    ]
    native = next((str(p) for p in candidates if p.exists()), None)
    python_available = shutil.which('python3') or shutil.which('python')
    preferred = 'native' if native else 'python' if python_available else 'prebuilt-native-required'
    unused = []
    if preferred == 'native': unused.append('python runtime is optional for deployed common tools')
    if preferred == 'python': unused.append('native binary is optional but recommended for Python-free hosts')
    return {'os': system, 'arch': arch, 'preferred_implementation': preferred, 'native_binary_path': native, 'python_executable_path': python_available, 'unused_variants': unused}


def analyze(root: Path) -> dict[str, object]:
    paths = list(walk(root))
    langs = Counter()
    non_language_files = 0
    stat_error_count = 0
    large_files = 0
    for p in paths:
        lang = LANG.get(p.suffix.lower())
        if lang is None:
            non_language_files += 1
        else:
            langs[lang] += 1
        try:
            if p.stat().st_size >= 100_000:
                large_files += 1
        except OSError:
            stat_error_count += 1

    size = 'small' if len(paths) < 200 else 'medium' if len(paths) < 2000 else 'large'
    hay = ' '.join(str(p.relative_to(root)).lower() for p in paths)
    types = [k for k, words in TYPE_SIGNALS.items() if any(w in hay for w in words)]
    docs = [p for p in paths if p.suffix.lower() in {'.md','.rst','.txt'}]
    tests = [p for p in paths if 'test' in p.name.lower() or any(x.lower() in {'test','tests'} for x in p.parts)]
    git_repository_present = (root / '.git').exists()
    git_executable_available = bool(shutil.which('git'))
    git_status = 'not_repository'
    dirty = None
    if git_repository_present and git_executable_available:
        ok, text = git_result(root,'status','--porcelain')
        git_status = 'ok' if ok else 'query_failed'
        dirty = bool(text) if ok else None
    elif git_repository_present:
        git_status = 'git_unavailable'
    external = [x for x in EXTERNAL if shutil.which(x)]
    runtime_plan = implementation_plan(root)

    techniques = ['AI_CONTEXT minimum core','Search-first / Read-second','Exploration stop condition','Source of Truth','Targeted validation']
    tools = ['common/small/doc-index','common/small/file-role-map','common/small/environment-plan']
    if git_repository_present:
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
    if {'game','gui'} & set(types): techniques.append('Headless-first + visual confirmation when required')
    if 'simulation' in types: techniques.append('Deterministic seam / structured observation')
    if 'packaged-app' in types: techniques.append('Artifact-boundary validation')
    for lang, _ in langs.most_common(3):
        if lang in {'python','csharp','go','c','cpp','gdscript'}:
            tools.append(f'{lang}/small')
            if size in {'medium','large'}: tools.append(f'{lang}/medium')
            if size == 'large': tools.append(f'{lang}/large')

    return {
        'tool': 'analyze-and-recommend',
        'status': 'ok',
        'project_root': str(root),
        'project_size_class': size,
        'files_scanned': len(paths),
        'scan_truncated': False,
        'recognized_source_files_scanned': sum(langs.values()),
        'non_language_files_scanned': non_language_files,
        'documentation_file_count': len(docs),
        'test_file_count': len(tests),
        'large_files_100kb_plus_count': large_files,
        'file_stat_error_count': stat_error_count,
        'language_file_counts': dict(langs.most_common()),
        'detected_project_types': types,
        'git': {
            'repository_present': git_repository_present,
            'executable_available': git_executable_available,
            'status': git_status,
            'dirty': dirty,
        },
        'external_tools_available': external,
        'runtime_plan': runtime_plan,
        'recommended_techniques': list(dict.fromkeys(techniques)),
        'recommended_tool_paths': list(dict.fromkeys(tools)),
    }


def main():
    ap = argparse.ArgumentParser(description='Analyze a repository and recommend Context Reducer techniques/tools as self-describing JSON.')
    ap.add_argument('root', nargs='?', default='.')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        out = {'tool': 'analyze-and-recommend', 'status': 'input_missing', 'project_root': str(root)}
    elif not root.is_dir():
        out = {'tool': 'analyze-and-recommend', 'status': 'input_not_directory', 'project_root': str(root)}
    else:
        out = analyze(root)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
