from __future__ import annotations

import subprocess
from pathlib import Path


# git_lines はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def git_lines(root: Path, args: list[str]) -> dict[str, object]:
    try:
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=False)
    except OSError:
        return {
            'ok': False,
            'lines': [],
            'error_kind': 'git_unavailable',
        }
    if result.returncode != 0:
        return {
            'ok': False,
            'lines': [],
            'error_kind': 'git_query_failed',
        }
    return {
        'ok': True,
        'lines': [line.strip() for line in result.stdout.splitlines() if line.strip()],
        'error_kind': None,
    }
