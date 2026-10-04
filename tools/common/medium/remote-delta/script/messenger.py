from __future__ import annotations

import subprocess
import shutil
from pathlib import Path


# git_result はGit queryの実行可否・stdout・error kindを呼び出し側へ返します。
def git_result(root: Path, *args: str) -> tuple[bool, str, str]:
    executable = shutil.which('git')
    if executable is None:
        return False, '', 'git_unavailable'
    try:
        result = subprocess.run(
            [executable, '-C', str(root), *args],
            capture_output=True,
            text=True,
        )
    except OSError:
        return False, '', 'git_unavailable'
    error_kind = '' if result.returncode == 0 else 'git_query_failed'
    if args[:3] == ('show-ref', '--verify', '--quiet') and result.returncode == 1:
        error_kind = 'remote_unavailable'
    return result.returncode == 0, result.stdout.strip(), error_kind
