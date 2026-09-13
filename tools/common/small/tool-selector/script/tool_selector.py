#!/usr/bin/env python3
import argparse
import json
import os
from collections import Counter
from pathlib import Path

IGNORE = {'.git', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist', '__pycache__', '.godot', 'vendor'}
LANG = {
    '.py': 'python', '.cs': 'csharp', '.go': 'go', '.c': 'c', '.h': 'c',
    '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.hpp': 'cpp', '.hh': 'cpp',
    '.gd': 'gdscript', '.rs': 'rust', '.js': 'javascript', '.ts': 'typescript', '.java': 'java'
}

TYPE_SIGNALS = {
    'game': {'project.godot', 'unityproject', 'game', 'assets', 'scenes'},
    'gui': {'ui', 'views', 'widgets', 'forms', 'mainwindow', 'window'},
    'compiler': {'lexer', 'parser', 'token', 'ast', 'compiler', 'interpreter', 'grammar'},
    'data_tool': {'dataset', 'etl', 'converter', 'export', 'importer', 'migration'},
    'packaged_app': {'installer', 'package', 'publish', 'release', 'dist'},
    'simulation': {'simulation', 'simulator', 'agent', 'physics', 'seed', 'random'},
    'rule_heavy': {'rules', 'specification', 'protocol', 'validator', 'legal', 'policy'},
}


def iter_files(root: Path):
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        current_path = Path(current)
        for name in sorted(names):
            yield current_path / name


def detect_types_from_relative_path(relative_path: str, detected: set[str]) -> None:
    low = relative_path.lower()
    for project_type, words in TYPE_SIGNALS.items():
        if project_type in detected:
            continue
        if any(word in low for word in words):
            detected.add(project_type)


def recommend(size, languages, project_types, docs, tests, has_git):
    recommended_tools = [
        'common/small/analyze-and-recommend',
        'common/small/repo-profile',
        'common/small/source-of-truth-candidates',
    ]
    conditional_tools = ['common/small/doc-index'] if docs else []
    recommended_groups = []
    conditional_groups = []

    if has_git:
        recommended_tools.append('common/medium/compact-diff')
        conditional_tools.extend([
            'common/medium/remote-delta',
            'common/medium/change-router',
            'common/medium/context-pack-builder',
        ])
    if tests:
        conditional_tools.extend(['common/medium/validation-plan', 'common/medium/compact-log'])
    if docs:
        conditional_tools.extend(['common/medium/acceptance-extractor', 'common/medium/exploration-stop-check'])
    if size in {'medium', 'large'}:
        recommended_tools.append('common/medium/change-router')
        conditional_tools.extend([
            'common/medium/responsibility-candidates',
            'common/medium/doc-duplicate-hints',
            'common/large/hotspot-report',
        ])
    if size == 'large':
        recommended_tools.extend([
            'common/large/context-manifest',
            'common/large/target-slice',
            'common/large/context-budget',
        ])
    if 'rule_heavy' in project_types:
        conditional_tools.append('common/medium/policy-index')

    for lang, _ in languages[:3]:
        if lang not in {'other', 'rust', 'javascript', 'typescript', 'java'}:
            recommended_groups.append(f'{lang}/small')
            if size in {'medium', 'large'}:
                conditional_groups.append(f'{lang}/medium')
            if size == 'large':
                conditional_groups.append(f'{lang}/large')
    if project_types:
        conditional_groups.append('profiles/project-type-profile')

    return (
        sorted(dict.fromkeys(recommended_tools)),
        sorted(dict.fromkeys(conditional_tools)),
        sorted(dict.fromkeys(recommended_groups)),
        sorted(dict.fromkeys(conditional_groups)),
    )


def build_selection(root: Path) -> dict[str, object]:
    languages = Counter()
    detected_types: set[str] = set()
    file_count = 0
    documentation_file_count = 0
    test_file_count = 0

    for path in iter_files(root):
        file_count += 1
        languages[LANG.get(path.suffix.lower(), 'other')] += 1
        if path.suffix.lower() in {'.md', '.rst', '.txt'}:
            documentation_file_count += 1
        relative = path.relative_to(root)
        if 'test' in path.name.lower() or 'tests' in {part.lower() for part in relative.parts}:
            test_file_count += 1
        detect_types_from_relative_path(relative.as_posix(), detected_types)

    size = 'small' if file_count < 200 else 'medium' if file_count < 2000 else 'large'
    project_types = sorted(detected_types)
    has_git = (root / '.git').exists()
    recommended_tools, conditional_tools, recommended_groups, conditional_groups = recommend(
        size,
        languages.most_common(),
        project_types,
        documentation_file_count,
        test_file_count,
        has_git,
    )
    return {
        'tool': 'tool-selector',
        'status': 'ok',
        'project_root': str(root),
        'project_size_class': size,
        'files_scanned': file_count,
        'scan_truncated': False,
        'language_file_counts': dict(languages.most_common()),
        'detected_project_types': project_types,
        'documentation_file_count': documentation_file_count,
        'test_file_count': test_file_count,
        'git_repository_detected': has_git,
        'recommended_tool_paths': recommended_tools,
        'conditional_tool_paths': conditional_tools,
        'recommended_tool_group_paths': recommended_groups,
        'conditional_tool_group_paths': conditional_groups,
    }


def main():
    parser = argparse.ArgumentParser(description='Select likely useful Context Reducer tools as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        result = {'tool': 'tool-selector', 'status': 'input_missing', 'project_root': str(root)}
    elif not root.is_dir():
        result = {'tool': 'tool-selector', 'status': 'input_not_directory', 'project_root': str(root)}
    else:
        result = build_selection(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
