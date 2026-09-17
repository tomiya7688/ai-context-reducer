#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

TOOL = 'cpp-symbols'
LANGUAGE = 'cpp'
EXTENSIONS = {'.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx', '.h'}
PATTERNS = [
    ('namespace', re.compile(r'^\s*namespace\s+([A-Za-z_]\w*)')),
    ('class', re.compile(r'^\s*(?:class|struct)\s+([A-Za-z_]\w*)')),
    ('func', re.compile(r'^\s*(?:template\s*<[^>]+>\s*)?(?:[\w:<>,~*&\[\]\s]+)\s+([A-Za-z_~]\w*)\s*\([^;]*\)\s*(?:const\s*)?(?:\{|$)')),
]


def scan(path: Path):
    try:
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError as exc:
        return {'file': str(path), 'status': 'read_failed', 'symbols': [], 'error': str(exc)}
    symbols = []
    for line_no, line in enumerate(lines, 1):
        for kind, pattern in PATTERNS:
            match = pattern.search(line)
            if match:
                symbols.append({'kind': kind, 'name': match.group(1), 'line': line_no})
                break
    return {'file': str(path), 'status': 'ok', 'symbols': symbols}


def build_result(paths):
    files, unsupported = [], []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            unsupported.append({'path': raw, 'reason': 'input_missing'})
        elif path.is_dir():
            files.extend(f for f in sorted(path.rglob('*')) if f.is_file() and f.suffix.lower() in EXTENSIONS)
        elif path.suffix.lower() in EXTENSIONS:
            files.append(path)
        else:
            unsupported.append({'path': raw, 'reason': 'unsupported_input'})
    rows = [scan(path) for path in sorted(dict.fromkeys(files), key=lambda p: p.as_posix())]
    read_errors = sum(row['status'] == 'read_failed' for row in rows)
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if read_errors or unsupported else 'ok',
        'language': LANGUAGE,
        'files': rows,
        'file_count': len(rows),
        'symbol_count': sum(len(row['symbols']) for row in rows),
        'parse_error_count': 0,
        'read_error_count': read_errors,
        'unsupported_input_count': len(unsupported),
        'unsupported_inputs': unsupported,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    print(json.dumps(build_result(args.paths), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
