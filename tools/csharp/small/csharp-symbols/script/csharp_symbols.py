#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

TOOL = 'csharp-symbols'
LANGUAGE = 'csharp'
PATTERNS = [
    ('namespace', re.compile(r'^\s*namespace\s+([A-Za-z_][\w\.]*)')),
    ('class', re.compile(r'^\s*(?:public|private|internal|protected|static|sealed|abstract|partial|\s)*\s*class\s+([A-Za-z_]\w*)')),
    ('interface', re.compile(r'^\s*(?:public|private|internal|protected|partial|\s)*\s*interface\s+([A-Za-z_]\w*)')),
    ('method', re.compile(r'^\s*(?:public|private|internal|protected|static|virtual|override|async|sealed|partial|extern|new|\s)+[\w<>,\[\]\.?]+\s+([A-Za-z_]\w*)\s*\(')),
]


# 1ファイルのsymbolだけを解析し、read/parse失敗を空symbol一覧と区別して返す。
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


# symbol解析結果とwarningを集約し、不完全なscanをclean扱いしない結果を作る。
def build_result(paths):
    files, unsupported = [], []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            unsupported.append({'path': raw, 'reason': 'input_missing'})
        elif path.is_dir():
            files.extend(
                f for f in sorted(path.rglob('*.cs'))
                if not any(part in {'bin', 'obj'} for part in f.parts)
            )
        elif path.suffix.lower() == '.cs':
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


# CLI入力を検証し、通常結果と失敗状態を同じ機械可読JSON契約で返す。
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    print(json.dumps(build_result(args.paths), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
