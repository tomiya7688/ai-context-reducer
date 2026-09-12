#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from pathlib import Path

IGNORE = {'.git', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist', '__pycache__', 'vendor'}
LANG = {
    '.py':'Python', '.cs':'CSharp', '.go':'Go', '.gd':'GDScript',
    '.cpp':'C++', '.cc':'C++', '.cxx':'C++', '.hpp':'C++', '.hh':'C++', '.hxx':'C++',
    '.c':'C', '.h':'C/C++ Header',
    '.rs':'Rust', '.js':'JavaScript', '.ts':'TypeScript', '.java':'Java'
}


def walk(root: Path):
    for p in root.rglob('*'):
        if any(part in IGNORE for part in p.parts):
            continue
        if p.is_file():
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    files = list(walk(root))
    langs = Counter(LANG.get(p.suffix.lower(), 'Other') for p in files)
    code_files = sum(v for k,v in langs.items() if k != 'Other')
    size = 'small' if len(files) < 200 else 'medium' if len(files) < 2000 else 'large'
    data = {
        'root': root.name,
        'files': len(files),
        'code_files': code_files,
        'project_size': size,
        'languages': dict(langs.most_common()),
        'top_dirs': sorted({p.relative_to(root).parts[0] for p in files if p.relative_to(root).parts})[:30],
    }
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"project={data['root']} size={size} files={len(files)} code_files={code_files}")
        print('languages=' + ', '.join(f'{k}:{v}' for k,v in langs.most_common()))
        print('top_dirs=' + ', '.join(data['top_dirs']))

if __name__ == '__main__':
    main()
