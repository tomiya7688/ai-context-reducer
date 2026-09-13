from __future__ import annotations

import subprocess
from pathlib import Path


def git_text(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ['git', '-C', str(root), *args],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ''
