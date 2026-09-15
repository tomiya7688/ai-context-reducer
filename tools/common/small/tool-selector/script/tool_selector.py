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


def item(path: str, reason: str) -> dict[str, str]:
    return {'tool_path': path, 'reason': reason}


def recommend(size, languages, project_types, docs, tests, has_git):
    recommended = [
        item('common/small/analyze-and-recommend', 'cheap first-pass repository guidance'),
        item('common/small/repo-profile', 'identify repository size and language mix'),
        item('common/small/source-of-truth-candidates', 'find likely authoritative documentation entry points'),
    ]
    conditional = []

    if docs:
        conditional.append(item('common/small/doc-index', 'documentation files are present; index headings before reading full documents'))
    if has_git:
        recommended.append(item('common/medium/compact-diff', 'Git repository detected; inspect bounded change evidence before full diff'))
        conditional.extend([
            item('common/medium/remote-delta', 'use when local/remote divergence matters'),
            item('common/medium/change-router', 'use when changed files need likely tests/docs routing'),
            item('common/medium/context-pack-builder', 'use when preparing a bounded task context pack'),
        ])
    if tests:
        conditional.extend([
            item('common/medium/validation-plan', 'test files detected; derive targeted validation from changed paths'),
            item('common/medium/compact-log', 'use when validation output is too large for agent context'),
        ])
    if docs:
        conditional.extend([
            item('common/medium/acceptance-extractor', 'use when task documents contain goal/acceptance sections'),
            item('common/medium/exploration-stop-check', 'use to decide whether broad exploration can stop'),
        ])
    if size in {'medium', 'large'}:
        recommended.append(item('common/medium/change-router', f'{size} repository benefits from change-to-test/doc routing'))
        conditional.extend([
            item('common/medium/responsibility-candidates', 'use to locate likely responsibility boundaries'),
            item('common/medium/doc-duplicate-hints', 'use when duplicated documentation may inflate context'),
            item('common/large/hotspot-report', 'use to find large/deep repository hotspots'),
        ])
    if size == 'large':
        recommended.extend([
            item('common/large/context-manifest', 'large repository benefits from prioritized context routing'),
            item('common/large/target-slice', 'read bounded excerpts instead of full files'),
            item('common/large/context-budget', 'estimate likely agent context cost before broad reads'),
            item('common/large/source-structure-index', 'reuse language-specific symbol/dependency analysis and expand only the target neighborhood'),
        ])
    if 'rule_heavy' in project_types:
        conditional.append(item('common/medium/policy-index', 'rule-heavy project detected; extract likely policy lines before reading full documents'))

    groups = []
    conditional_groups = []
    for lang, _ in languages[:3]:
        groups.append({'tool_group_path': f'{lang}/small', 'reason': f'{lang} source files detected'})
        if size in {'medium', 'large'}:
            conditional_groups.append({'tool_group_path': f'{lang}/medium', 'reason': f'{size} {lang} project may need dependency/change analysis'})
        if size == 'large':
            conditional_groups.append({'tool_group_path': f'{lang}/large', 'reason': f'large {lang} project may benefit from whole-scope analysis'})
    if project_types:
        conditional_groups.append({'tool_group_path': 'profiles/project-type-profile', 'reason': 'project-type signals were detected'})

    def dedupe(rows, key):
        out = []
        seen = set()
        for row in rows:
            value = row[key]
            if value in seen:
                continue
            seen.add(value)
            out.append(row)
        return out

    return dedupe(recommended, 'tool_path'), dedupe(conditional, 'tool_path'), dedupe(groups, 'tool_group_path'), dedupe(conditional_groups, 'tool_group_path')


def build_selection(root: Path) -> dict[str, object]:
    languages = Counter()
    detected_types: set[str] = set()
    file_count = 0
    non_language_files = 0
    documentation_file_count = 0
    test_file_count = 0

    for path in iter_files(root):
        file_count += 1
        language = LANG.get(path.suffix.lower())
        if language is None:
            non_language_files += 1
        else:
            languages[language] += 1
        if path.suffix.lower() in {'.md', '.rst', '.txt'}:
            documentation_file_count += 1
        relative = path.relative_to(root)
        if 'test' in path.name.lower() or 'tests' in {part.lower() for part in relative.parts}:
            test_file_count += 1
        detect_types_from_relative_path(relative.as_posix(), detected_types)

    size = 'small' if file_count < 200 else 'medium' if file_count < 2000 else 'large'
    project_types = sorted(detected_types)
    has_git = (root / '.git').exists()
    recommended, conditional, groups, conditional_groups = recommend(
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
        'recognized_source_files_scanned': sum(languages.values()),
        'non_language_files_scanned': non_language_files,
        'language_file_counts': dict(languages.most_common()),
        'detected_project_types': project_types,
        'documentation_file_count': documentation_file_count,
        'test_file_count': test_file_count,
        'git_repository_detected': has_git,
        'recommended_tools': recommended,
        'conditional_tools': conditional,
        'recommended_tool_groups': groups,
        'conditional_tool_groups': conditional_groups,
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
