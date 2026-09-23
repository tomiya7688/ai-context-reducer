from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ERROR_TEXT_LIMIT = 1200
CTAGS_EXCLUDES = (
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'bin', 'obj', 'build', 'dist', '.godot', '.idea', '.vs', 'vendor', 'generated',
)


# 外部backendの長いerrorをboundedにし、診断情報だけをcontextへ残す。
def _bounded_error(text: str, fallback: str) -> str:
    value = text.strip() or fallback
    return value if len(value) <= ERROR_TEXT_LIMIT else value[:ERROR_TEXT_LIMIT]


# JSON入力を明示的に読み、形式不正を空入力と混同しない。
def load_json(path: str) -> object:
    return json.loads(Path(path).read_text(encoding='utf-8'))


# JSON Linesを1行ずつ読み、ctags等のstream出力をboundedに受け取る。
def load_json_lines(path: str) -> list[object]:
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f'invalid JSON line {number}: {exc}') from exc
    return rows


# 共通index結果を単一JSON表現で出力し、表現の重複を避ける。
def write_json(path: str, payload: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


# SCIP CLI結果を取得し、backend不在や失敗を明示した構造で返す。
def scip_print_json(path: str) -> dict[str, object]:
    executable = shutil.which('scip')
    if not executable:
        return {
            'ok': False,
            'status': 'backend_unavailable',
            'backend': 'scip',
            'error': 'scip executable was not found on PATH',
        }

    result = subprocess.run(
        [executable, 'print', '--json', path],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return {
            'ok': False,
            'status': 'command_failed',
            'backend': 'scip',
            'exit_code': result.returncode,
            'error': _bounded_error(result.stderr, 'scip print failed'),
        }
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {
            'ok': False,
            'status': 'invalid_backend_output',
            'backend': 'scip',
            'error': str(exc),
        }
    return {'ok': True, 'status': 'ok', 'backend': 'scip', 'payload': payload}


# ctags JSON Linesを取得し、backend失敗を握り潰さず正規化前へ渡す。
def ctags_json(path: str) -> dict[str, object]:
    executable = shutil.which('ctags')
    if not executable:
        return {
            'ok': False,
            'status': 'backend_unavailable',
            'backend': 'ctags',
            'error': 'ctags executable was not found on PATH',
        }

    probe = subprocess.run(
        [executable, '--list-output-formats'],
        text=True,
        capture_output=True,
        check=False,
    )
    formats = {token.strip().lower() for token in probe.stdout.replace('\t', ' ').split()}
    if probe.returncode != 0 or 'json' not in formats:
        return {
            'ok': False,
            'status': 'backend_incompatible',
            'backend': 'ctags',
            'error': 'installed ctags does not advertise Universal Ctags JSON output support',
        }

    command = [
        executable,
        '--output-format=json',
        '--fields=+nSlesp',
        '--recurse=yes',
        '-o', '-',
    ]
    command.extend(f'--exclude={name}' for name in CTAGS_EXCLUDES)
    command.append(path)
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return {
            'ok': False,
            'status': 'command_failed',
            'backend': 'ctags',
            'exit_code': result.returncode,
            'error': _bounded_error(result.stderr, 'ctags JSON generation failed'),
        }

    rows = []
    for number, line in enumerate(result.stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            return {
                'ok': False,
                'status': 'invalid_backend_output',
                'backend': 'ctags',
                'error': f'invalid JSON line {number}: {exc}',
            }
    return {'ok': True, 'status': 'ok', 'backend': 'ctags', 'payload': rows}
