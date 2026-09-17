#!/usr/bin/env python3
import argparse
import json
import os
import shutil
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
EXTERNAL_CANDIDATES = ('rg', 'fd', 'ast-grep', 'sg', 'ctags', 'scip', 'tree-sitter', 'scc', 'git-sizer')
PHASE_ORDER = {'orient': 0, 'search': 1, 'scope': 2, 'inspect': 3, 'validate': 4, 'stop': 5}


def iter_files(root: Path):
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.lower() not in IGNORE)
        current_path = Path(current)
        for name in sorted(names):
            yield current_path / name


def detect_types_from_relative_path(relative_path: str, detected: set[str]) -> None:
    low = relative_path.lower()
    for project_type, words in TYPE_SIGNALS.items():
        if project_type not in detected and any(word in low for word in words):
            detected.add(project_type)


def available_external_tools() -> set[str]:
    return {name for name in EXTERNAL_CANDIDATES if shutil.which(name)}


def item(path: str, reason: str, phase: str = 'orient', activation: str = 'always', availability: str = 'ready') -> dict[str, str]:
    return {'tool_path': path, 'phase': phase, 'activation': activation, 'availability': availability, 'reason': reason}


def _availability(path: str, external: set[str]) -> str:
    if path == 'common/small/text-search':
        return 'external_backend_ready' if 'rg' in external else 'portable_fallback_ready'
    if path == 'common/small/path-find':
        return 'external_backend_ready' if 'fd' in external else 'portable_fallback_ready'
    if path in {'common/small/repo-profile', 'common/small/repo-stats'}:
        return 'external_backend_ready' if 'scc' in external else 'portable_fallback_ready'
    if path == 'common/medium/structural-search':
        return 'external_backend_ready' if {'ast-grep', 'sg'} & external else 'python_ast_fallback_limited'
    return 'ready'


def _dedupe_and_sort(rows, key):
    out, seen = [], set()
    for row in rows:
        value = row[key]
        if value not in seen:
            seen.add(value)
            out.append(row)
    return sorted(out, key=lambda row: PHASE_ORDER.get(row.get('phase', 'orient'), 99))


def recommend(size, languages, project_types, docs, tests, has_git, external_tools=None):
    external = set(external_tools or ())
    recommended = [
        item('common/small/repo-profile', 'identify repository size and language mix before deeper reads', 'orient', availability=_availability('common/small/repo-profile', external)),
        item('common/small/source-of-truth-candidates', 'find likely authoritative documentation entry points before broad reading', 'orient'),
        item('common/small/text-search', 'search for target terms before opening whole files', 'search', availability=_availability('common/small/text-search', external)),
        item('common/small/path-find', 'narrow candidate paths before tree-wide reading', 'search', availability=_availability('common/small/path-find', external)),
    ]
    conditional = []
    if docs:
        conditional.append(item('common/small/doc-index', 'documentation exists; inspect headings before full documents', 'search', 'when documentation is relevant'))
    if has_git:
        recommended.append(item('common/medium/compact-diff', 'Git repository detected; inspect bounded change evidence before full diff', 'scope', 'when the task concerns current changes'))
        conditional.extend([
            item('common/medium/remote-delta', 'compare local and remote state before broad repository exploration', 'scope', 'when remote divergence matters'),
            item('common/medium/change-router', 'route changed files to likely tests and documentation', 'scope', 'when changed files are known'),
            item('common/medium/context-pack-builder', 'materialize a bounded task context when context must be handed off', 'inspect', 'when a reusable Context Pack is needed'),
        ])
        if size == 'large' and 'git-sizer' in external:
            conditional.append(item('common/small/git-history-health', 'reuse existing git-sizer for compact history/object health findings', 'orient', 'when repository history/object size may affect work', 'external_backend_ready'))
    if tests:
        conditional.extend([
            item('common/medium/validation-plan', 'derive targeted validation from changed paths instead of running everything first', 'validate', 'when implementation changes are ready to validate'),
            item('common/medium/compact-log', 'compress large validation output to actionable findings', 'validate', 'when validation output is verbose'),
        ])
    if docs:
        conditional.extend([
            item('common/medium/acceptance-extractor', 'extract Goal/Required/Acceptance before implementation when task docs contain them', 'orient', 'when a task/specification document exists'),
            item('common/medium/exploration-stop-check', 'check whether enough task context exists to stop broad exploration', 'stop', 'after Goal/Required/Acceptance/source/tests are identified'),
        ])
    if size in {'medium', 'large'}:
        recommended.append(item('common/medium/change-router', f'{size} repository benefits from change-to-test/doc routing', 'scope', 'when changed files are known'))
        conditional.extend([
            item('common/medium/structural-search', 'use syntax-shaped search when text search is noisy', 'search', 'when text search returns unrelated matches', _availability('common/medium/structural-search', external)),
            item('common/medium/responsibility-candidates', 'locate likely responsibility boundaries before reading neighboring modules', 'scope', 'when ownership boundaries are unclear'),
            item('common/medium/doc-duplicate-hints', 'find duplicated documentation that may inflate context', 'orient', 'when documentation is repetitive'),
            item('common/large/hotspot-report', 'find large/deep hotspots before broad source reads', 'orient', 'when repository shape is unclear'),
        ])
    if size == 'large':
        recommended.extend([
            item('common/large/context-manifest', 'prioritize likely context entry points in a large repository', 'orient'),
            item('common/large/source-structure-index', 'query and expand only the target symbol/dependency neighborhood', 'scope'),
            item('common/large/target-slice', 'read bounded excerpts instead of full source files', 'inspect'),
            item('common/large/context-budget', 'estimate likely agent context cost before broad reads', 'orient'),
        ])
    if 'tree-sitter' in external and languages:
        conditional.append(item('common/small/syntax-health', 'reuse configured Tree-sitter parsers to surface only files with syntax issues', 'validate', 'when syntax-level validation is useful', 'external_backend_ready'))
    if 'rule_heavy' in project_types:
        conditional.append(item('common/medium/policy-index', 'extract likely policy lines before reading full rule documents', 'orient', 'when policy/rule constraints govern the task'))

    groups, conditional_groups = [], []
    for lang, _ in languages[:3]:
        groups.append({'tool_group_path': f'{lang}/small', 'phase': 'search', 'reason': f'{lang} source files detected'})
        if size in {'medium', 'large'}:
            conditional_groups.append({'tool_group_path': f'{lang}/medium', 'phase': 'scope', 'reason': f'{size} {lang} project may need dependency/change analysis'})
        if size == 'large':
            conditional_groups.append({'tool_group_path': f'{lang}/large', 'phase': 'scope', 'reason': f'large {lang} project may benefit from whole-scope analysis'})
    if project_types:
        conditional_groups.append({'tool_group_path': 'profiles/project-type-profile', 'phase': 'orient', 'reason': 'project-type signals were detected'})
    return (_dedupe_and_sort(recommended, 'tool_path'), _dedupe_and_sort(conditional, 'tool_path'), _dedupe_and_sort(groups, 'tool_group_path'), _dedupe_and_sort(conditional_groups, 'tool_group_path'))


def apply_task_context(recommended, conditional, *, goal: str, task_file: str | None, changed_files: list[str], validation_intent: str):
    if not (goal or task_file or changed_files or validation_intent != 'unknown'):
        return recommended, conditional, {'applied': False}

    all_rows = {row['tool_path']: row for row in recommended + conditional}
    selected_paths = set()
    reasons = []
    if goal:
        selected_paths.update({'common/small/text-search', 'common/small/path-find'})
        reasons.append('goal_provided')
    if task_file:
        selected_paths.update({'common/medium/acceptance-extractor', 'common/small/doc-index', 'common/medium/exploration-stop-check'})
        reasons.append('task_file_provided')
    if changed_files:
        selected_paths.update({'common/medium/compact-diff', 'common/medium/change-router', 'common/large/source-structure-index', 'common/large/target-slice'})
        reasons.append('changed_files_provided')
    if validation_intent in {'targeted', 'full'}:
        selected_paths.update({'common/medium/validation-plan', 'common/small/syntax-health'})
        reasons.append(f'validation_{validation_intent}')

    selected = []
    for path in selected_paths:
        row = all_rows.get(path)
        if row is not None:
            selected.append({**row, 'task_relevance': 'direct'})
    selected = _dedupe_and_sort(selected, 'tool_path')
    deferred_count = len({row['tool_path'] for row in recommended + conditional}) - len(selected)
    return selected, [], {
        'applied': True,
        'goal_present': bool(goal),
        'task_file': task_file,
        'changed_files': changed_files,
        'validation_intent': validation_intent,
        'routing_reasons': reasons,
        'deferred_tool_count': max(0, deferred_count),
    }


def build_selection(root: Path, *, goal: str = '', task_file: str | None = None, changed_files: list[str] | None = None, validation_intent: str = 'unknown') -> dict[str, object]:
    languages = Counter()
    detected_types: set[str] = set()
    file_count = non_language_files = documentation_file_count = test_file_count = 0
    for path in iter_files(root):
        file_count += 1
        language = LANG.get(path.suffix.lower())
        if language is None: non_language_files += 1
        else: languages[language] += 1
        if path.suffix.lower() in {'.md', '.rst', '.txt'}: documentation_file_count += 1
        relative = path.relative_to(root)
        name, parts = path.name.lower(), {part.lower() for part in relative.parts}
        if name.startswith('test_') or name.endswith('_test.py') or name.endswith('_test.go') or {'test', 'tests'} & parts: test_file_count += 1
        detect_types_from_relative_path(relative.as_posix(), detected_types)

    size = 'small' if file_count < 200 else 'medium' if file_count < 2000 else 'large'
    project_types = sorted(detected_types)
    has_git = (root / '.git').exists()
    external = available_external_tools()
    recommended, conditional, groups, conditional_groups = recommend(size, languages.most_common(), project_types, documentation_file_count, test_file_count, has_git, external)
    normalized_changed = [Path(value).as_posix() for value in (changed_files or [])]
    recommended, conditional, task_context = apply_task_context(recommended, conditional, goal=goal.strip(), task_file=task_file, changed_files=normalized_changed, validation_intent=validation_intent)
    return {
        'tool': 'tool-selector', 'status': 'ok', 'project_root': str(root), 'project_size_class': size,
        'files_scanned': file_count, 'scan_truncated': False,
        'recognized_source_files_scanned': sum(languages.values()), 'non_language_files_scanned': non_language_files,
        'language_file_counts': dict(languages.most_common()), 'detected_project_types': project_types,
        'documentation_file_count': documentation_file_count, 'test_file_count': test_file_count,
        'git_repository_detected': has_git, 'external_tools_available': sorted(external),
        'routing_order': ['orient', 'search', 'scope', 'inspect', 'validate', 'stop'],
        'task_context': task_context,
        'exploration_stop_conditions': [
            'Goal, Required, and Acceptance are known',
            'authoritative source or implementation target is identified',
            'targeted validation path is identified',
            'additional broad exploration is unlikely to change the working set',
        ],
        'recommended_tools': recommended, 'conditional_tools': conditional,
        'recommended_tool_groups': groups, 'conditional_tool_groups': conditional_groups,
    }


def main():
    parser = argparse.ArgumentParser(description='Select an ordered Context Reducer routing plan as self-describing JSON.')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--goal', default='', help='Current task goal. Enables task-aware routing when provided.')
    parser.add_argument('--task-file', help='Task/specification document path used to prioritize acceptance and stop checks.')
    parser.add_argument('--changed', action='append', default=[], help='Known changed file. Repeat for multiple paths.')
    parser.add_argument('--validation-intent', choices=('unknown', 'targeted', 'full', 'none'), default='unknown')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists(): result = {'tool': 'tool-selector', 'status': 'input_missing', 'project_root': str(root)}
    elif not root.is_dir(): result = {'tool': 'tool-selector', 'status': 'input_not_directory', 'project_root': str(root)}
    else: result = build_selection(root, goal=args.goal, task_file=args.task_file, changed_files=args.changed, validation_intent=args.validation_intent)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
