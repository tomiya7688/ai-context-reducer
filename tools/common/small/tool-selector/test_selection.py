import importlib.util
from collections import Counter
from pathlib import Path

MODULE = Path(__file__).parent / 'script' / 'tool_selector.py'
spec = importlib.util.spec_from_file_location('tool_selector', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_recommend_for_large_python_repo():
    recommended, conditional = mod.recommend(
        'large',
        Counter({'python': 100}).most_common(),
        ['rule_heavy'],
        docs=5,
        tests=10,
        has_git=True,
    )
    assert 'common/large/context-budget' in recommended
    assert 'python/large' in conditional
    assert 'common/medium/policy-index' in conditional


def test_build_selection(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'tests').mkdir()
    (tmp_path / 'main.py').write_text('print(1)', encoding='utf-8')
    (tmp_path / 'tests' / 'test_main.py').write_text('def test_x(): pass', encoding='utf-8')
    (tmp_path / 'README.md').write_text('# Docs', encoding='utf-8')
    result = mod.build_selection(tmp_path)
    assert result['status'] == 'ok'
    assert result['test_file_count'] == 1
    assert 'common/medium/compact-diff' in result['recommended_tools']
