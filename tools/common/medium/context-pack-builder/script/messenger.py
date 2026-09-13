from __future__ import annotations

import subprocess
from pathlib import Path


def git_lines(root: Path, args: list[str]) -> list[str]:
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
