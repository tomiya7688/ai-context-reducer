#!/usr/bin/env python3
import argparse
import json
import subprocess


# run_git はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def run_git(*args: str) -> tuple[bool, str]:
    result = subprocess.run(['git', *args], text=True, capture_output=True, check=False)
    return result.returncode == 0, result.stdout.strip()


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    parser = argparse.ArgumentParser(description='Return compact Git diff evidence as self-describing JSON.')
    parser.add_argument('--base', default='HEAD~1')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--max-lines', type=int, default=120)
    args = parser.parse_args()

    log_ok, commits = run_git('log', '--oneline', f'{args.base}..{args.head}')
    files_ok, changed = run_git('diff', '--name-status', args.base, args.head)
    stat_ok, shortstat = run_git('diff', '--shortstat', args.base, args.head)
    diff_ok, diff_text = run_git('diff', '--unified=2', args.base, args.head)

    if not all((log_ok, files_ok, stat_ok, diff_ok)):
        result = {
            'tool': 'compact-diff',
            'status': 'git_query_failed',
            'base': args.base,
            'head': args.head,
        }
    else:
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


if __name__ == '__main__':
    main()
