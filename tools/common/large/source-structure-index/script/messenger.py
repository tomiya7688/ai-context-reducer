from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def load_json(path: str) -> object:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path: str, payload: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


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
            'error': result.stderr.strip() or 'scip print failed',
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
