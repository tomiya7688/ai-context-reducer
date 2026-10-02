#!/usr/bin/env python3
"""Compare native and Python language-run root validation in release smoke."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON_TOOL = ROOT / 'tools/common/small/language-run/script/language_run.py'


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def check(label: str, completed: subprocess.CompletedProcess[str], status: str, code: int) -> dict:
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(f'{label}: invalid JSON output: {completed.stdout!r}') from error
    if completed.returncode != code or payload.get('status') != status:
        raise AssertionError(
            f'{label}: exit={completed.returncode}, status={payload.get("status")}, '
            f'stdout={completed.stdout!r}, stderr={completed.stderr!r}'
        )
    return payload


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('usage: language_run_root_e2e.py <acr-toolbox>')
    binary = str(Path(sys.argv[1]).resolve())
    with tempfile.TemporaryDirectory(prefix='acr-language-run-root-e2e-') as raw:
        temp = Path(raw)
        roots = (
            (temp / 'missing', 'input_missing', 2),
            (temp / 'project.txt', 'input_not_directory', 2),
            (temp / 'empty', 'ok', 0),
        )
        roots[1][0].write_text('not a directory', encoding='utf-8')
        roots[2][0].mkdir()

        for root, expected_status, expected_code in roots:
            native = run([binary, 'language-run', str(root)])
            python = run([sys.executable, str(PYTHON_TOOL), str(root)])
            native_payload = check(f'native {root.name}', native, expected_status, expected_code)
            python_payload = check(f'Python {root.name}', python, expected_status, expected_code)
            for field in ('status', 'failure_count', 'skip_count', 'results'):
                if native_payload.get(field) != python_payload.get(field):
                    raise AssertionError(
                        f'{root.name}: native/Python {field} differs: '
                        f'{native_payload.get(field)!r} != {python_payload.get(field)!r}'
                    )

        if (roots[2][0] / '.acr' / 'language').exists():
            raise AssertionError('empty project scan unexpectedly created analyzer output')

    print('language-run root semantics match between native and Python tools.')


if __name__ == '__main__':
    main()
