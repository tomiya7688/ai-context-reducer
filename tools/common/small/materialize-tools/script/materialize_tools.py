#!/usr/bin/env python3
import argparse
import json
import platform
import shutil
from pathlib import Path


def choose(source: Path):
    system = platform.system().lower()
    native_name = 'acr-toolbox.exe' if system == 'windows' else 'acr-toolbox'
    native = source / 'tools' / 'bin' / native_name
    python = shutil.which('python3') or shutil.which('python') or shutil.which('py')
    selected = []
    if native.exists():
        selected.append((native, Path(native_name)))
        mode = 'native'
    elif python:
        selected += [
            (source / 'tools' / 'common' / 'small' / 'analyze-and-recommend' / 'script' / 'analyze_and_recommend.py', Path('analyze_and_recommend.py')),
            (source / 'tools' / 'common' / 'small' / 'text-search' / 'script' / 'text_search.py', Path('text_search.py')),
            (source / 'tools' / 'common' / 'small' / 'path-find' / 'script' / 'path_find.py', Path('path_find.py')),
            (source / 'tools' / 'common' / 'small' / 'tree-view' / 'script' / 'tree_view.py', Path('tree_view.py')),
            (source / 'tools' / 'common' / 'small' / 'repo-stats' / 'script' / 'repo_stats.py', Path('repo_stats.py')),
        ]
        mode = 'python'
    else:
        mode = 'unavailable'
    wrapper = source / 'tools' / ('analyze.bat' if system == 'windows' else 'analyze.sh')
    if wrapper.exists():
        selected.append((wrapper, Path(wrapper.name)))
    return mode, [(a,b) for a,b in selected if a.exists()]


def main():
    ap = argparse.ArgumentParser(description='Materialize only usable portable tool variants into a deployment directory.')
    ap.add_argument('source', nargs='?', default='.')
    ap.add_argument('--out', required=True)
    ap.add_argument('--apply', action='store_true', help='Copy files. Default is dry-run.')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    source = Path(args.source).resolve()
    out = Path(args.out).resolve()
    mode, selected = choose(source)
    result = {'mode': mode, 'output': str(out), 'files': [str(dst) for _,dst in selected], 'applied': False}
    if args.apply:
        out.mkdir(parents=True, exist_ok=True)
        for src, rel in selected:
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        result['applied'] = True
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"mode={mode} output={out} applied={result['applied']}")
        for rel in result['files']:
            print('  ' + rel)
        if not args.apply:
            print('dry-run: use --apply to copy selected variants')

if __name__ == '__main__':
    main()
