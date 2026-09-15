from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def find_ast_grep() -> str | None:
    direct = shutil.which('ast-grep')
    if direct:
        return direct
    candidate = shutil.which('sg')
    if not candidate:
        return None
    try:
        probe = subprocess.run([candidate, '--version'], text=True, capture_output=True, check=False, timeout=2)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (probe.stdout + '\n' + probe.stderr).lower()
    return candidate if 'ast-grep' in text else None


def run_ast_grep(executable: str, root: Path, pattern: str, language: str | None) -> tuple[bool, list[dict], str]:
    command = [
        executable,
        'run',
        '--pattern',
        pattern,
        '--json=compact',
        '--color',
        'never',
    ]
    if language:
        command.extend(['--lang', language])
    command.append(str(root))
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=False)
    except OSError as exc:
        return False, [], str(exc)
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).strip()
        return False, [], diagnostic[:500]
    if not result.stdout.strip():
        return True, [], ''
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False, [], 'ast-grep returned invalid JSON'
    if not isinstance(payload, list):
        return False, [], 'ast-grep returned unexpected JSON shape'
    return True, payload, ''
