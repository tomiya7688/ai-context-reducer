#!/usr/bin/env python3
import argparse
import json
import os
import platform
import shutil
from pathlib import Path

OPTIONAL = ['rg', 'fd', 'git', 'python', 'python3', 'go']


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
    native = next((str(p) for p in native_candidates if p.exists()), None)
    return {
        'os': system,
        'arch': machine,
        'python': python_cmd,
        'git': commands.get('git'),
        'optional_tools': {k: v for k, v in commands.items() if k not in {'python','python3','git','go'} and v},
        'go': commands.get('go'),
        'native_toolbox': native,
    }


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


def main():
    ap = argparse.ArgumentParser(description='Plan portable ai-context-reducer tool implementations for this environment.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    info = probe(root)
    out = {'environment': info, 'plan': plan(info)}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    print(f"os={info['os']} arch={info['arch']}")
    print(f"python={info['python'] or 'unavailable'} git={info['git'] or 'unavailable'} native={info['native_toolbox'] or 'unavailable'}")
    print('keep:')
    for x in out['plan']['keep']:
        print(f'  - {x}')
    if out['plan']['fallback']:
        print('fallback:')
        for x in out['plan']['fallback']:
            print(f'  - {x}')
    for x in out['plan']['notes']:
        print(f'note: {x}')

if __name__ == '__main__':
    main()
