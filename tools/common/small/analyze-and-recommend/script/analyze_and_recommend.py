#!/usr/bin/env python3
import argparse
import json
import os
import platform
import shutil
import subprocess
from collections import Counter
from pathlib import Path

IGNORE = {'.git','.venv','venv','node_modules','bin','obj','build','dist','__pycache__','.godot','.cache','vendor'}
LANG = {'.py':'python','.cs':'csharp','.go':'go','.c':'c','.h':'c','.cpp':'cpp','.cc':'cpp','.cxx':'cpp','.hpp':'cpp','.hh':'cpp','.gd':'gdscript','.rs':'rust','.js':'javascript','.ts':'typescript','.java':'java'}
TYPE_SIGNALS = {
    'game': {'project.godot','assets','scenes','game'},
    'gui': {'ui','views','widgets','forms','window'},
    'compiler': {'lexer','parser','token','ast','compiler','grammar'},
    'data_tool': {'dataset','etl','converter','export','importer','migration'},
    'packaged_app': {'installer','package','publish','release','dist'},
    'simulation': {'simulation','simulator','agent','physics','seed','random'},
    'rule_heavy': {'rules','specification','protocol','validator','policy'},
}
EXTERNAL = ['rg','fd','ast-grep','sg','ctags','scip','tree-sitter','scc','git-sizer']


def walk(root):
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        current_path = Path(current)
        for name in sorted(names):
            yield current_path / name


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
    return {
        'os': system,
        'arch': arch,
        'preferred_implementation': preferred,
        'native_binary_path': native,
        'python_executable_path': python_available,
    }


def is_test_path(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    name = path.name.lower()
    parts = {part.lower() for part in relative.parts}
    return name.startswith('test_') or name.endswith('_test.py') or name.endswith('_test.go') or bool({'test', 'tests'} & parts)


def analyze(root: Path) -> dict[str, object]:
    paths = list(walk(root))
    langs = Counter()
    non_language_files = 0
    stat_error_count = 0
    large_files = 0
    detected_types = set()
    docs = 0
    tests = 0

    for p in paths:
        lang = LANG.get(p.suffix.lower())
        if lang is None:
            non_language_files += 1
        else:
            langs[lang] += 1
        if p.suffix.lower() in {'.md','.rst','.txt'}:
            docs += 1
        if is_test_path(p, root):
            tests += 1
        relative = p.relative_to(root).as_posix().lower()
        for project_type, words in TYPE_SIGNALS.items():
            if any(word in relative for word in words):
                detected_types.add(project_type)
        try:
            if p.stat().st_size >= 100_000:
                large_files += 1
        except OSError:
            stat_error_count += 1

    size = 'small' if len(paths) < 200 else 'medium' if len(paths) < 2000 else 'large'
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

    external = [name for name in EXTERNAL if shutil.which(name)]
    status = 'ok_with_warnings' if stat_error_count else 'ok'
    return {
        'tool': 'analyze-and-recommend',
        'status': status,
        'project_root': str(root),
        'project_size_class': size,
        'files_scanned': len(paths),
        'scan_truncated': False,
        'recognized_source_files_scanned': sum(langs.values()),
        'non_language_files_scanned': non_language_files,
        'documentation_file_count': docs,
        'test_file_count': tests,
        'large_files_100kb_plus_count': large_files,
        'file_stat_error_count': stat_error_count,
        'language_file_counts': dict(langs.most_common()),
        'detected_project_types': sorted(detected_types),
        'git': {
            'repository_present': git_repository_present,
            'executable_available': git_executable_available,
            'status': git_status,
            'dirty': dirty,
        },
        'external_tools_available': external,
        'runtime_plan': implementation_plan(root),
        'routing_handoff': {
            'tool_path': 'common/small/tool-selector',
            'native_command': 'acr-toolbox select',
            'reason': 'tool-selector is the Source of Truth for ordered tool routing and exploration-stop conditions',
        },
    }


def main():
    ap = argparse.ArgumentParser(description='Analyze repository/runtime facts, then hand off ordered tool routing to tool-selector.')
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
