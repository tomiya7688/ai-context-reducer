#!/usr/bin/env python3
import argparse
import json
import shutil

TOOLS = {
    'rg': 'fast text search / search-first workflow',
    'fd': 'fast file discovery respecting ignore rules',
    'ast-grep': 'AST-based structural search and rewrite',
    'ctags': 'multi-language symbol index',
    'tree-sitter': 'parser infrastructure for precise syntax analysis',
    'scc': 'fast code size / language / complexity overview',
    'git-sizer': 'Git repository size and history health metrics',
    'semgrep': 'multi-language static analysis / policy checks',
}


def main():
    ap = argparse.ArgumentParser(description='Probe useful external context-reduction tools on PATH.')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    rows = []
    for exe, purpose in TOOLS.items():
        path = shutil.which(exe)
        rows.append({'tool': exe, 'available': bool(path), 'path': path, 'purpose': purpose})
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            mark = 'OK' if row['available'] else '--'
            print(f"{mark:>2} {row['tool']:<12} {row['purpose']}")

if __name__ == '__main__':
    main()
