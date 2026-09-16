import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'repo_profile.py'
spec = importlib.util.spec_from_file_location('repo_profile', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_build_profile_separates_language_and_other_files(tmp_path):
    (tmp_path / 'main.py').write_text('print(1)\n', encoding='utf-8')
    (tmp_path / 'README.md').write_text('# Demo\n', encoding='utf-8')
    result = module.build_profile(tmp_path, 0)
    assert result['tool'] == 'repo-profile'
    assert result['status'] == 'ok'
    assert result['backend'] == 'portable'
    assert result['files_scanned'] == 2
    assert result['language_file_counts'] == {'Python': 1}
    assert result['recognized_source_files_scanned'] == 1
    assert result['non_language_files_scanned'] == 1
    assert result['scan_truncated'] is False
    assert result['language_metrics'][0]['lines'] is None


def test_build_profile_marks_only_real_truncation_unknown(tmp_path):
    (tmp_path / 'a.py').write_text('', encoding='utf-8')
    exact = module.build_profile(tmp_path, 1)
    assert exact['scan_truncated'] is False
    assert exact['project_size_class'] == 'small'

    (tmp_path / 'b.py').write_text('', encoding='utf-8')
    truncated = module.build_profile(tmp_path, 1)
    assert truncated['scan_truncated'] is True
    assert truncated['project_size_class'] == 'large_or_unknown_due_to_scan_limit'


def test_parse_scc_payload_keeps_compact_language_metrics():
    counts, metrics = module.parse_scc_payload([
        {
            'Name': 'Go',
            'Count': 3,
            'Lines': 120,
            'Code': 90,
            'Comment': 20,
            'Blank': 10,
            'Complexity': 7,
            'Files': [{'Location': 'should-not-be-forwarded.go'}],
        },
        {
            'Name': 'Python',
            'Count': 1,
            'Lines': 30,
            'Code': 20,
            'Comment': 5,
            'Blank': 5,
            'Complexity': 2,
        },
    ])
    assert counts == {'Go': 3, 'Python': 1}
    assert metrics == [
        {'language': 'Go', 'files': 3, 'lines': 120, 'code': 90, 'comment': 20, 'blank': 10, 'complexity': 7},
        {'language': 'Python', 'files': 1, 'lines': 30, 'code': 20, 'comment': 5, 'blank': 5, 'complexity': 2},
    ]
