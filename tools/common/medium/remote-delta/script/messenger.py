from __future__ import annotations

import subprocess
from pathlib import Path


# git_result はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def git_result(root: Path, *args: str) -> tuple[bool, str]:
    result = subprocess.run(
        ['git', '-C', str(root), *args],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout.strip()
