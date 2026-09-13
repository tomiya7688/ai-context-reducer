import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'file_role_map.py'
spec = importlib.util.spec_from_file_location('file_role_map', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_role_classification():
    assert module.role(Path('src/main.py')) == 'source'
    assert module.role(Path('tests/test_main.py')) == 'tests'
    assert module.role(Path('docs/guide.md')) == 'documentation'
    assert module.role(Path('config/app.toml')) == 'configuration'


def test_build_role_map_limits_examples(tmp_path):
    (tmp_path / 'a.py').write_text('', encoding='utf-8')
    (tmp_path / 'b.py').write_text('', encoding='utf-8')
    result = module.build_role_map(tmp_path, 0, 1)
    source = result['roles']['source']
    assert source['file_count'] == 2
    assert len(source['example_paths']) == 1
    assert result['scan_truncated'] is False
