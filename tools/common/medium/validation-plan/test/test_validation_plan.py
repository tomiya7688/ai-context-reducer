import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'validation_plan.py'
spec = importlib.util.spec_from_file_location('validation_plan', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_python_file_recommends_tests_and_syntax_check():
    result = module.classify('src/example.py')
    assert 'targeted tests' in result
    assert 'syntax/build check' in result


def test_parser_path_adds_contract_validation():
    result = module.classify('src/parser/example.py')
    assert 'targeted regression tests' in result
    assert 'contract/spec check' in result
