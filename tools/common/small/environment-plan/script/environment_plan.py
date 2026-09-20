#!/usr/bin/env python3
import argparse
import json
import platform
import shutil
from pathlib import Path

TOOL = 'environment-plan'
OPTIONAL = ['rg', 'fd', 'git', 'python', 'python3', 'go']


# probe は対象scopeを調べ、routingに必要な情報だけを集める。
def probe(root: Path):
    system = platform.system().lower()
    machine = platform.machine().lower()
    commands = {name: shutil.which(name) for name in OPTIONAL}
    python_cmd = commands.get('python3') or commands.get('python')
    native_name = 'acr-toolbox.exe' if system == 'windows' else 'acr-toolbox'
    native_candidates = [
        root / 'tools' / 'bin' / native_name,
        root / native_name,
    ]
    native = next((str(path) for path in native_candidates if path.exists()), None)
    return {
        'os': system,
        'arch': machine,
        'python': python_cmd,
        'git': commands.get('git'),
        'optional_tools': {
            key: value
            for key, value in commands.items()
            if key not in {'python', 'python3', 'git', 'go'} and value
        },
        'go': commands.get('go'),
        'native_toolbox': native,
    }


# plan はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def plan(info):
    keep = []
    fallback = []
    notes = []
    if info['native_toolbox']:
        keep.append('native/acr-toolbox')
    elif info['python']:
        keep.append('python scripts')
        fallback.append('build/download acr-toolbox for Python-free environments')
    else:
        fallback.append('prebuilt acr-toolbox required')
    if info['optional_tools'].get('rg'):
        keep.append('external rg for fast search')
    else:
        keep.append('built-in text-search fallback')
    if info['optional_tools'].get('fd'):
        keep.append('external fd for fast path search')
    else:
        keep.append('built-in path-find fallback')
    if not info['git']:
        notes.append('Git-dependent delta tools unavailable; keep non-Git analysis only.')
    return {'keep': keep, 'fallback': fallback, 'notes': notes}


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    parser = argparse.ArgumentParser(description='Plan portable ai-context-reducer tool implementations for this environment.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--json', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    info = probe(root)
    output = {
        'tool': TOOL,
        'status': 'ok',
        'root_path': str(root),
        'environment': info,
        'plan': plan(info),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
