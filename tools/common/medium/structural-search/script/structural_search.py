#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from commander import search_structure


def main():
    parser = argparse.ArgumentParser(description='Run bounded structural search with ast-grep when available and a stdlib Python AST fallback.')
    parser.add_argument('pattern', help='AST-style pattern, for example: print($ARG)')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--lang', dest='language', help='Language hint for ast-grep. Python fallback accepts python/py only.')
    parser.add_argument('--backend', choices=['auto', 'ast-grep', 'fallback'], default='auto')
    parser.add_argument('--max-results', type=int, default=40, help='Maximum matches returned to the caller. 0 means unlimited.')
    args = parser.parse_args()

    result = search_structure(
        Path(args.root).resolve(),
        args.pattern,
        args.language,
        max(0, args.max_results),
        args.backend,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
