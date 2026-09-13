import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'acceptance_extractor.py'
spec = importlib.util.spec_from_file_location('acceptance_extractor', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_section_stops_at_next_heading():
    lines = ['# Goal', 'first', 'second', '# Acceptance', 'done']
    values, truncated = module.section(lines, 0, 40)
    assert values == ['first', 'second']
    assert truncated is False


def test_section_reports_truncation():
    lines = ['# Goal', 'one', 'two', 'three']
    values, truncated = module.section(lines, 0, 2)
    assert values == ['one', 'two']
    assert truncated is True
