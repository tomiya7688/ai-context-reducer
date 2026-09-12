#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


def git_lines(root, args):
    r = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    return [x.strip() for x in r.stdout.splitlines() if x.strip()] if r.returncode == 0 else []


def main():
    ap = argparse.ArgumentParser(description='Generate a small task Context Pack skeleton from git state.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--goal', default='')
    ap.add_argument('--required', default='')
    ap.add_argument('--acceptance', default='')
    ap.add_argument('--deferred', default='')
    ap.add_argument('--output')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    changed = git_lines(root, ['diff', '--name-only', 'HEAD'])[:60]
    status = git_lines(root, ['status', '--short'])[:60]
    text = f'''# Context Pack\n\n## Task\n- Goal: {args.goal}\n- Required: {args.required}\n- Acceptance: {args.acceptance}\n- Deferred / out of scope: {args.deferred}\n\n## Working Set\n- Changed files:\n'''
    text += ''.join(f'  - {x}\n' for x in changed) or '  - none detected\n'
    text += '\n## Git Status\n' + (''.join(f'- {x}\n' for x in status) or '- clean / unavailable\n')
    text += '\n## Required Constraints\n- \n\n## Validation\n- Targeted evidence:\n- Unverified areas:\n\n## Rules\n- Search first, read second.\n- Stop broad exploration once Goal / Required / Acceptance / Deferred are sufficiently clear.\n- Read full diffs or large docs only when needed.\n'
    if args.output:
        Path(args.output).write_text(text, encoding='utf-8')
    else:
        print(text, end='')

if __name__ == '__main__':
    main()
