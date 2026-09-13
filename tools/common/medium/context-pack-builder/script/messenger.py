from __future__ import annotations

import subprocess
from pathlib import Path


def git_lines(root: Path, args: list[str]) -> dict[str, object]:
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    return {
        'ok': result.returncode == 0,
        'lines': [line.strip() for line in result.stdout.splitlines() if line.strip()] if result.returncode == 0 else [],
    }
