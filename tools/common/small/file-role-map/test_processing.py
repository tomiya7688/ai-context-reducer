import importlib.util
from pathlib import Path

MODULE = Path(__file__).parent / 'script' / 'file_role_map.py'
spec = importlib.util.spec_from_file_location('file_role_map', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_role_classification():
    assert mod.role(Path('src/main.py')) == 'source'
    assert mod.role(Path('tests/test_main.py')) == 'tests'
    assert mod.role(Path('docs/guide.md')) == 'documentation'
    assert mod.role(Path('config/app.toml')) == 'configuration'


def test_build_role_map(tmp_path):
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src' / 'a.py').write_text('x = 1', encoding='utf-8')
    (tmp_path / 'README.md').write_text('doc', encoding='utf-8')
    result = mod.build_role_map(tmp_path, 0, 2)
    assert result['status'] == 'ok'
    assert result['files_scanned'] == 2
    assert result['roles']['source']['file_count'] == 1
    assert result['roles']['documentation']['file_count'] == 1
