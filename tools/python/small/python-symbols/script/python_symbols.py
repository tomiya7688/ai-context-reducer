#!/usr/bin/env python3
import argparse
import ast
import json
from pathlib import Path

TOOL = 'python-symbols'
LANGUAGE = 'python'


# Python ASTから関数・class宣言と位置を取り出し、構文errorを空結果と区別します。
def scan(path: Path):
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        return {'file': str(path), 'status': 'read_failed', 'symbols': [], 'error': str(exc)}
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {'file': str(path), 'status': 'parse_failed', 'symbols': [], 'error': str(exc)}
    symbols = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.append({'kind': type(node).__name__, 'name': node.name, 'line': node.lineno})
    symbols.sort(key=lambda row: row['line'])
    return {'file': str(path), 'status': 'ok', 'symbols': symbols}


# Python入力pathをsource fileへ展開し、存在しないrootと未対応拡張子を別warningにします。
def collect(paths):
    files = []
    unsupported = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            unsupported.append({'path': raw, 'reason': 'input_missing'})
        elif path.is_dir():
            files.extend(f for f in sorted(path.rglob('*.py')) if '__pycache__' not in f.parts)
        elif path.suffix.lower() == '.py':
            files.append(path)
        else:
            unsupported.append({'path': raw, 'reason': 'unsupported_input'})
    rows = [scan(path) for path in sorted(dict.fromkeys(files), key=lambda p: p.as_posix())]
    return rows, unsupported


# Python sourceごとのAST結果を統合し、syntax failureがあればpartial statusを残します。
def build_result(paths):
    rows, unsupported = collect(paths)
    parse_errors = sum(row['status'] == 'parse_failed' for row in rows)
    read_errors = sum(row['status'] == 'read_failed' for row in rows)
    warnings = parse_errors + read_errors + len(unsupported)
    return {
        'tool': TOOL,
        'status': 'ok_with_warnings' if warnings else 'ok',
        'language': LANGUAGE,
        'files': rows,
        'file_count': len(rows),
        'symbol_count': sum(len(row['symbols']) for row in rows),
        'parse_error_count': parse_errors,
        'read_error_count': read_errors,
        'unsupported_input_count': len(unsupported),
        'unsupported_inputs': unsupported,
    }


# main はPython rootと出力先を検証し、symbol一覧とper-file parse statusを返します。
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    print(json.dumps(build_result(args.paths), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
