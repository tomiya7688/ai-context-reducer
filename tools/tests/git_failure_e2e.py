#!/usr/bin/env python3
"""Compare portable native/Python Git failure statuses against local fixtures."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPACT_DIFF = ROOT / 'tools/common/medium/compact-diff/script/compact_diff.py'
REMOTE_DELTA = ROOT / 'tools/common/medium/remote-delta/script/remote_delta.py'


def run(args: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)


def check_python_result(label: str, completed: subprocess.CompletedProcess[str], status: str, code: int) -> None:
    payload = json.loads(completed.stdout)
    if completed.returncode != code or payload.get('status') != status:
        raise AssertionError(f'{label}: exit={completed.returncode}, status={payload.get("status")}, output={completed.stdout!r}, stderr={completed.stderr!r}')


def check_native_result(label: str, completed: subprocess.CompletedProcess[str], status: str, code: int) -> None:
    output = completed.stdout + completed.stderr
    if completed.returncode != code or status not in output:
        raise AssertionError(f'{label}: exit={completed.returncode}, expected status={status}, output={output!r}')


def git(root: Path, *args: str) -> None:
    completed = run(['git', '-C', str(root), *args])
    if completed.returncode:
        raise RuntimeError(f'git {args!r} failed: {completed.stderr}')


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('usage: git_failure_e2e.py <acr-toolbox>')
    binary = Path(sys.argv[1]).resolve()
    if not binary.is_file():
        raise FileNotFoundError(binary)

    with tempfile.TemporaryDirectory(prefix='acr-git-failure-e2e-') as raw:
        temp = Path(raw)
        non_repo = temp / 'not-a-repository'
        non_repo.mkdir()
        repo = temp / 'fixture'
        repo.mkdir()
        git(repo, 'init')
        git(repo, 'config', 'user.name', 'Release E2E')
        git(repo, 'config', 'user.email', 'release-e2e@example.invalid')
        (repo / 'README.md').write_text('# fixture\n', encoding='utf-8')
        git(repo, 'add', 'README.md')
        git(repo, 'commit', '-m', 'fixture')
        git(repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')

        for command, python_script, native_args, python_args in (
            ('compact-diff', COMPACT_DIFF, [str(non_repo), 'HEAD', 'HEAD'], ['--base', 'HEAD', '--head', 'HEAD']),
            ('remote-delta', REMOTE_DELTA, [str(non_repo), 'origin/main', 'HEAD'], [str(non_repo), '--remote', 'origin/main', '--base', 'HEAD']),
        ):
            native = run([str(binary), command, *native_args])
            check_native_result(f'{command} non-repository', native, 'git_unavailable_or_not_repository', 2)
            python_cwd = non_repo if command == 'compact-diff' else repo
            python = run([sys.executable, str(python_script), *python_args], cwd=python_cwd)
            check_python_result(f'{command} non-repository', python, 'git_unavailable_or_not_repository', 2)

        native = run([str(binary), 'compact-diff', str(repo), 'HEAD', 'HEAD'])
        python = run([sys.executable, str(COMPACT_DIFF), '--base', 'HEAD', '--head', 'HEAD'], cwd=repo)
        if native.returncode != 0 or '(none)' not in native.stdout or python.returncode != 0:
            raise AssertionError(f'clean empty diff should succeed: native={native.stderr!r}, python={python.stdout!r}')
        payload = json.loads(python.stdout)
        if payload['status'] != 'ok' or payload['changed_files']:
            raise AssertionError('Python clean empty diff did not return status=ok')

        for command, python_script, native_args, python_args in (
            ('compact-diff', COMPACT_DIFF, [str(repo), 'missing-base', 'HEAD'], ['--base', 'missing-base', '--head', 'HEAD']),
            ('compact-diff', COMPACT_DIFF, [str(repo), 'HEAD', 'missing-head'], ['--base', 'HEAD', '--head', 'missing-head']),
            ('remote-delta', REMOTE_DELTA, [str(repo), 'origin/main', 'missing-base'], [str(repo), '--remote', 'origin/main', '--base', 'missing-base']),
        ):
            native = run([str(binary), command, *native_args])
            check_native_result(f'{command} invalid revision', native, 'git_query_failed', 2)
            python = run([sys.executable, str(python_script), *python_args], cwd=repo)
            check_python_result(f'{command} invalid revision', python, 'git_query_failed', 2)

        native = run([str(binary), 'remote-delta', str(repo), 'origin/missing', 'HEAD'])
        python = run([sys.executable, str(REMOTE_DELTA), str(repo), '--remote', 'origin/missing', '--base', 'HEAD'], cwd=repo)
        check_native_result('remote-delta missing remote', native, 'remote_unavailable', 0)
        check_python_result('remote-delta missing remote', python, 'remote_unavailable', 0)

        no_git_env = dict(os.environ)
        no_git_env['PATH'] = ''
        native = run([str(binary), 'compact-diff', str(repo), 'HEAD', 'HEAD'], env=no_git_env)
        python = run([sys.executable, str(COMPACT_DIFF), '--base', 'HEAD', '--head', 'HEAD'], cwd=repo, env=no_git_env)
        check_native_result('compact-diff Git unavailable', native, 'git_unavailable', 2)
        check_python_result('compact-diff Git unavailable', python, 'git_unavailable', 2)

        native = run([str(binary), 'remote-delta', str(repo), 'origin/main', 'HEAD'], env=no_git_env)
        python = run([sys.executable, str(REMOTE_DELTA), str(repo), '--remote', 'origin/main', '--base', 'HEAD'], cwd=repo, env=no_git_env)
        check_native_result('remote-delta Git unavailable', native, 'git_unavailable', 2)
        check_python_result('remote-delta Git unavailable', python, 'git_unavailable', 2)

    print('Git failure semantics match between native and Python tools.')


if __name__ == '__main__':
    main()
