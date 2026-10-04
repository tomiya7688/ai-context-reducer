import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).parents[1] / 'script' / 'validation_plan.py'
spec = importlib.util.spec_from_file_location('validation_plan', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ValidationPlanTests(unittest.TestCase):
    # test_python_file_recommends_tests_and_syntax_check はPython変更に対応するtestとsyntax actionを選ぶことを確認します。
    def test_python_file_recommends_tests_and_syntax_check(self):
        result = module.classify('src/example.py')
        self.assertIn('targeted tests', result)
        self.assertIn('syntax/build check', result)

    # test_parser_path_adds_contract_validation はparser変更にcontract validationを追加することを確認します。
    def test_parser_path_adds_contract_validation(self):
        result = module.classify('src/parser/example.py')
        self.assertIn('targeted regression tests', result)
        self.assertIn('contract/spec check', result)

    # test_build_path_is_not_misclassified_as_ui はbuildというpath片をUI判定に使わないことを確認します。
    def test_build_path_is_not_misclassified_as_ui(self):
        result = module.classify('build/core.py')
        self.assertNotIn('visual confirmation when acceptance is visual', result)
        self.assertIn('targeted tests', result)

    # test_compound_names_are_tokenized は複合file名がvalidation keywordへ分解されることを確認します。
    def test_compound_names_are_tokenized(self):
        result = module.classify('tools/parser_rules.py')
        self.assertIn('contract/spec check', result)


if __name__ == '__main__':
    unittest.main()
