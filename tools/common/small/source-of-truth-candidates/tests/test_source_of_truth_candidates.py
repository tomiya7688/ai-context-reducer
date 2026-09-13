import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'source_of_truth_candidates.py'
spec = importlib.util.spec_from_file_location('source_of_truth_candidates', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_candidate_paths_group_by_role(tmp_path):
    (tmp_path / 'architecture.md').write_text('# A\n', encoding='utf-8')
    (tmp_path / 'specification.md').write_text('# S\n', encoding='utf-8')
    candidates, truncated = module.candidate_paths(tmp_path, 10)
    assert candidates['architecture'] == ['architecture.md']
    assert candidates['specification'] == ['specification.md']
    assert truncated['architecture'] is False


def test_candidate_paths_report_role_truncation(tmp_path):
    (tmp_path / 'architecture-a.md').write_text('', encoding='utf-8')
    (tmp_path / 'architecture-b.md').write_text('', encoding='utf-8')
    candidates, truncated = module.candidate_paths(tmp_path, 1)
    assert len(candidates['architecture']) == 1
    assert truncated['architecture'] is True
