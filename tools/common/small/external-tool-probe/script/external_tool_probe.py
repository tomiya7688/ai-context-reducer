#!/usr/bin/env python3
import argparse
import json
import shutil

TOOL = 'external-tool-probe'
TOOLS = {
    'rg': 'fast text search / search-first workflow',
    'fd': 'fast file discovery respecting ignore rules',
    'ast-grep': 'AST-based structural search and rewrite',
    'ctags': 'multi-language symbol index',
    'scip': 'language-agnostic semantic index export',
    'tree-sitter': 'parser infrastructure for precise syntax analysis',
    'scc': 'fast code size / language / complexity overview',
    'git-sizer': 'Git repository size and history health metrics',
}


def main():
    parser = argparse.ArgumentParser(description='Probe useful external context-reduction tools on PATH.')
    parser.add_argument('--json', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    rows = []
    available = 0
    for executable, purpose in TOOLS.items():
        path = shutil.which(executable)
        is_available = bool(path)
        available += is_available
        rows.append({
            'name': executable,
            'available': is_available,
            'path': path,
            'purpose': purpose,
        })
    print(json.dumps({
        'tool': TOOL,
        'status': 'ok',
        'probed_tool_count': len(rows),
        'available_tool_count': available,
        'external_tools': rows,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
