#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

TOOL = 'c-symbols'
LANGUAGE = 'c'
EXTENSIONS = {'.c', '.h'}
FUNC = re.compile(r'^\s*(?!if\b|for\b|while\b|switch\b)(?:[A-Za-z_]\w*[\s\*]+)+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{?\s*$')
TYPE = re.compile(r'^\s*(?:typedef\s+)?(?:struct|enum|union)\s+([A-Za-z_]\w*)')


def scan(path: Path):
    try:
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError as exc:
        return {'file': str(path), 'status': 'read_failed', 'symbols': [], 'error': str(exc)}
    symbols = []
    for line_no, line in enumerate(lines, 1):
        match = TYPE.search(line)
        if match:
            symbols.append({'kind': 'type', 'name': match.group(1), 'line': line_no})
            continue
        match = FUNC.search(line)
        if match:
            symbols.append({'kind': 'func', 'name': match.group(1), 'line': line_no})
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
