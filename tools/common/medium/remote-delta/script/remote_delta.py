#!/usr/bin/env python3
import argparse, subprocess
from pathlib import Path

def run(root, *args):
    try:
        return subprocess.check_output(['git','-C',str(root),*args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ''

def main():
    ap=argparse.ArgumentParser(description='Show compact local/remote git delta without dumping a full diff.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--base', default='HEAD')
    ap.add_argument('--remote', default='origin/HEAD')
    ap.add_argument('--max-files', type=int, default=40)
    args=ap.parse_args(); root=Path(args.root).resolve()
    status=run(root,'status','--short')
    remote=run(root,'rev-parse','--verify',args.remote)
    if not remote:
        print('remote=unavailable')
        print('local_changes=' + ('yes' if status else 'no'))
        return
    ahead=run(root,'rev-list','--count',f'{args.remote}..{args.base}')
    behind=run(root,'rev-list','--count',f'{args.base}..{args.remote}')
    names=run(root,'diff','--name-only',args.base,args.remote).splitlines()
    stat=run(root,'diff','--shortstat',args.base,args.remote)
    commits=run(root,'log','--oneline','--max-count=8',f'{args.base}..{args.remote}')
    print(f'ahead={ahead or 0} behind={behind or 0} dirty={"yes" if status else "no"}')
    if stat: print('diff=' + stat)
    print('changed_files:')
    for n in names[:args.max_files]: print('  ' + n)
    if len(names)>args.max_files: print(f'  ... truncated {len(names)-args.max_files} more')
    if commits:
        print('remote_commits:')
        for line in commits.splitlines(): print('  ' + line)

if __name__=='__main__': main()
