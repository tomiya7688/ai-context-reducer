import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'repo_profile.py'
spec = importlib.util.spec_from_file_location('repo_profile', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_build_profile_reports_language_counts(tmp_path):
    (tmp_path / 'main.py').write_text('print(1)\n', encoding='utf-8')
    (tmp_path / 'README.md').write_text('# Demo\n', encoding='utf-8')
    result = module.build_profile(tmp_path, 0)
    assert result['tool'] == 'repo-profile'
    assert result['status'] == 'ok'
    assert result['files_scanned'] == 2
    assert result['language_file_counts']['Python'] == 1
    assert result['scan_truncated'] is False


def test_build_profile_marks_truncated_size_unknown(tmp_path):
    (tmp_path / 'a.py').write_text('', encoding='utf-8')
    (tmp_path / 'b.py').write_text('', encoding='utf-8')
    result = module.build_profile(tmp_path, 1)
    assert result['scan_truncated'] is True
    assert result['project_size_class'] == 'large-or-unknown'
