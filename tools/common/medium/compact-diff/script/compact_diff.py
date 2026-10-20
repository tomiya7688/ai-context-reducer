#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess


# run_git はGit subprocessのstdout・stderr・終了状態を呼び出し側へ返します。
def run_git(*args: str) -> tuple[bool, str, str]:
    executable = shutil.which('git')
    if executable is None:
        return False, '', 'git_unavailable'
    try:
        result = subprocess.run([executable, *args], text=True, capture_output=True, check=False)
    except OSError:
        return False, '', 'git_unavailable'
    error_kind = '' if result.returncode == 0 else 'git_query_failed'
    return result.returncode == 0, result.stdout.strip(), error_kind


# main はGit diffを取得してchange summaryへ圧縮し、query failureを区別します。
def main():
    parser = argparse.ArgumentParser(description='Return compact Git diff evidence as self-describing JSON.')
    parser.add_argument('--base', default='HEAD~1')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--max-lines', type=int, default=120)
    args = parser.parse_args()
    if args.max_lines < 0:
        parser.error('--max-lines must be non-negative')

    repository_ok, _, repository_error = run_git('rev-parse', '--is-inside-work-tree')
    if not repository_ok:
        error_kind = 'git_unavailable' if repository_error == 'git_unavailable' else 'git_unavailable_or_not_repository'
        query_results = []
    else:
        query_results = [
            run_git('log', '--oneline', f'{args.base}..{args.head}'),
            run_git('diff', '--name-status', args.base, args.head),
            run_git('diff', '--shortstat', args.base, args.head),
            run_git('diff', '--unified=2', args.base, args.head),
        ]
        error_kind = 'git_query_failed' if not all(result[0] for result in query_results) else ''

    if error_kind:
        result = {
            'tool': 'compact-diff',
            'status': error_kind,
            'base': args.base,
            'head': args.head,
        }
    else:
        commits, changed, shortstat, diff_text = (result[1] for result in query_results)
        diff_lines = diff_text.splitlines()
        result = {
            'tool': 'compact-diff',
            'status': 'ok',
            'base': args.base,
            'head': args.head,
            'commits': [line for line in commits.splitlines() if line],
            'changed_files': [line for line in changed.splitlines() if line],
            'diff_stat': shortstat or None,
            'diff_lines': diff_lines[:args.max_lines],
            'diff_truncated': len(diff_lines) > args.max_lines,
            'diff_total_lines': len(diff_lines),
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'ok' else 2


if __name__ == '__main__':
    raise SystemExit(main())
