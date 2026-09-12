#!/usr/bin/env python3
import argparse
import subprocess


def run(*args):
    return subprocess.run(args, text=True, capture_output=True, check=False).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='HEAD~1')
    ap.add_argument('--head', default='HEAD')
    ap.add_argument('--max-lines', type=int, default=120)
    args = ap.parse_args()

    print('## commits')
    print(run('git','log','--oneline',f'{args.base}..{args.head}') or '(none)')
    print('\n## changed files')
    print(run('git','diff','--name-status',args.base,args.head) or '(none)')
    print('\n## shortstat')
    print(run('git','diff','--shortstat',args.base,args.head) or '(none)')
    print('\n## bounded diff')
    diff = run('git','diff','--unified=2',args.base,args.head).splitlines()
    for line in diff[:args.max_lines]:
        print(line)
    if len(diff) > args.max_lines:
        print(f'... TRUNCATED {len(diff)-args.max_lines} lines; inspect full diff only if needed')

if __name__ == '__main__':
    main()
