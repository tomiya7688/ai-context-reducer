#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

NAMES = {
    'architecture': ('architecture', 'design', '設計'),
    'specification': ('spec', 'specification', '仕様'),
    'coding_rules': ('coding', 'rules', 'style', '規約'),
    'ai_context': ('ai_context', 'agents', 'claude'),
    'current_state': ('state', 'status', 'current'),
    'tasks': ('roadmap', 'backlog', 'todo', 'issue', '予定'),
}
DOC_EXTS = {'.md', '.txt', '.rst'}
SKIP = {'.git', '.venv', 'venv', 'node_modules', 'build', 'dist', 'bin', 'obj', '__pycache__', 'vendor'}


def candidate_paths(root: Path, per_role_limit: int) -> tuple[dict[str, list[str]], dict[str, bool]]:
    hits = {key: [] for key in NAMES}
    truncated = {key: False for key in NAMES}
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            if path.suffix.lower() not in DOC_EXTS:
                continue
            low = name.lower()
            rel = path.relative_to(root).as_posix()
            for role, words in NAMES.items():
                if not any(word in low for word in words):
                    continue
                if len(hits[role]) < per_role_limit:
                    hits[role].append(rel)
                else:
                    truncated[role] = True
    for values in hits.values():
        values.sort()
    return hits, truncated


def main():
    parser = argparse.ArgumentParser(description='Find filename-based source-of-truth candidates as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--per-role-limit', type=int, default=20)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        result = {'tool': 'source-of-truth-candidates', 'status': 'input_missing', 'project_root': str(root)}
    elif not root.is_dir():
        result = {'tool': 'source-of-truth-candidates', 'status': 'input_not_directory', 'project_root': str(root)}
    else:
        candidates, truncated = candidate_paths(root, max(0, args.per_role_limit))
        result = {
            'tool': 'source-of-truth-candidates',
            'status': 'ok',
            'project_root': str(root),
            'authority': 'candidate_only_not_verified_source_of_truth',
            'candidates_by_role': candidates,
            'candidates_truncated_by_role': truncated,
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
