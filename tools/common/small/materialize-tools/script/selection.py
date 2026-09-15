from __future__ import annotations

import platform
import shutil
from pathlib import Path

PYTHON_TOOL_PATHS = [
    Path('common/small/analyze-and-recommend/script/analyze_and_recommend.py'),
    Path('common/small/text-search/script/text_search.py'),
    Path('common/small/path-find/script/path_find.py'),
    Path('common/small/tree-view/script/tree_view.py'),
    Path('common/small/repo-stats/script/repo_stats.py'),
]


def choose(source: Path, system: str | None = None, python_executable: str | None = None) -> tuple[str, list[dict[str, object]]]:
    tools_root = source / 'tools'
    system_name = (system or platform.system()).lower()
    native_name = 'acr-toolbox.exe' if system_name == 'windows' else 'acr-toolbox'
    native = tools_root / 'bin' / native_name
    python = python_executable
    if python is None:
        python = shutil.which('python3') or shutil.which('python') or shutil.which('py')

    selected: list[dict[str, object]] = []
    if native.exists():
        selected.append({
            'source': native,
            'destination': Path('bin') / native_name,
            'role': 'native_toolbox',
        })
        mode = 'native'
    elif python:
        for relative in PYTHON_TOOL_PATHS:
            selected.append({
                'source': tools_root / relative,
                'destination': relative,
                'role': 'python_tool',
            })
        mode = 'python'
    else:
        mode = 'unavailable'

    wrapper = tools_root / ('analyze.bat' if system_name == 'windows' else 'analyze.sh')
    if mode != 'unavailable' and wrapper.exists():
        selected.append({
            'source': wrapper,
            'destination': Path(wrapper.name),
            'role': 'entry_wrapper',
        })

    return mode, selected
