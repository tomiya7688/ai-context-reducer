import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'tool_selector.py'
spec = importlib.util.spec_from_file_location('tool_selector', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def paths(rows, key):
    return [row[key] for row in rows]


def test_recommend_includes_git_tools_with_reasons():
    recommended, conditional, recommended_groups, conditional_groups = module.recommend(
        'small', [('python', 3)], [], docs=0, tests=0, has_git=True
    )
    assert 'common/medium/compact-diff' in paths(recommended, 'tool_path')
    assert 'common/medium/remote-delta' in paths(conditional, 'tool_path')
    assert 'python/small' in paths(recommended_groups, 'tool_group_path')
    assert conditional_groups == []
    assert all(row['reason'] for row in recommended + conditional)


def test_build_selection_separates_language_and_other_files(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'main.py').write_text('print(1)\n', encoding='utf-8')
    (tmp_path / 'README.md').write_text('# demo\n', encoding='utf-8')
    result = module.build_selection(tmp_path)
    assert result['tool'] == 'tool-selector'
    assert result['status'] == 'ok'
    assert result['git_repository_detected'] is True
    assert result['language_file_counts'] == {'python': 1}
    assert result['recognized_source_files_scanned'] == 1
    assert result['non_language_files_scanned'] == 1
    assert result['scan_truncated'] is False


def test_project_type_detection_uses_relative_path_content():
    detected = set()
    module.detect_types_from_relative_path('src/parser/token_stream.py', detected)
    assert 'compiler' in detected
    assert 'simulation' not in detected


def test_large_rule_heavy_repo_gets_large_and_policy_tools():
    recommended, conditional, recommended_groups, conditional_groups = module.recommend(
        'large', [('python', 100)], ['rule_heavy'], docs=5, tests=10, has_git=True
    )
    assert 'common/large/context-manifest' in paths(recommended, 'tool_path')
    assert 'common/medium/policy-index' in paths(conditional, 'tool_path')
    assert 'python/small' in paths(recommended_groups, 'tool_group_path')
    assert 'python/large' in paths(conditional_groups, 'tool_group_path')
