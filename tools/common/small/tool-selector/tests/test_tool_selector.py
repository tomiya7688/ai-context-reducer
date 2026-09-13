import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'tool_selector.py'
spec = importlib.util.spec_from_file_location('tool_selector', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_recommend_includes_git_tools():
    recommended, conditional, recommended_groups, conditional_groups = module.recommend(
        'small', [('python', 3)], [], docs=0, tests=0, has_git=True
    )
    assert 'common/medium/compact-diff' in recommended
    assert 'common/medium/remote-delta' in conditional
    assert 'python/small' in recommended_groups
    assert conditional_groups == []


def test_build_selection_is_self_describing(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'main.py').write_text('print(1)\n', encoding='utf-8')
    result = module.build_selection(tmp_path)
    assert result['tool'] == 'tool-selector'
    assert result['status'] == 'ok'
    assert result['git_repository_detected'] is True
    assert result['language_file_counts']['python'] == 1
    assert result['scan_truncated'] is False


def test_project_type_detection_uses_relative_path_content():
    detected = set()
    module.detect_types_from_relative_path('src/parser/token_stream.py', detected)
    assert 'compiler' in detected
    assert 'simulation' not in detected


def test_large_rule_heavy_repo_gets_large_and_policy_tools():
    recommended, conditional, recommended_groups, conditional_groups = module.recommend(
        'large', [('python', 100), ('other', 20)], ['rule_heavy'], docs=5, tests=10, has_git=True
    )
    assert 'common/large/context-manifest' in recommended
    assert 'common/medium/policy-index' in conditional
    assert 'python/small' in recommended_groups
    assert 'python/large' in conditional_groups
