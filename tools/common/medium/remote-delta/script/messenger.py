from __future__ import annotations

import subprocess
from pathlib import Path


def git_result(root: Path, *args: str) -> tuple[bool, str]:
    result = subprocess.run(
        ['git', '-C', str(root), *args],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout.strip()
