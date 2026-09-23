import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'affected_tests.py'
spec = importlib.util.spec_from_file_location('affected_tests', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AffectedTestsContractTests(unittest.TestCase):
# このケースで安全側routingとエラー契約が回帰していないことを検証する。
    def test_dependency_map_consumers_add_candidates(self):
        dep_map = {
            'files': [
                {'file': 'src/app/loader.py', 'status': 'ok', 'imports': ['pkg.parser.lexer']},
            ],
            'scan_truncated': False,
        }
        result = module.analyze(['pkg/parser/lexer.py'], {}, dep_map, True)
        self.assertTrue(result['dependency_map']['used'])
        self.assertTrue(result['dependency_map']['complete'])
        self.assertIn('dependency-map consumers: 1', result['reasons'])

# このケースで安全側routingとエラー契約が回帰していないことを検証する。
    def test_incomplete_dependency_map_forces_broader_fallback(self):
        dep_map = {
            'files': [],
            'scan_truncated': True,
            'parse_error_count': 2,
        }
        result = module.analyze(
            ['src/parser/lexer.py'],
            {'mappings': [{'source': 'src/parser/*', 'tests': ['tests/test_parser.py']}]},
            dep_map,
            True,
        )
        self.assertEqual('ok_with_warnings', result['status'])
        self.assertTrue(result['impact_uncertain'])
        self.assertEqual('medium', result['confidence'])
        self.assertEqual('broader-or-full', result['fallback'])
        self.assertIn('dependency_map_truncated', result['dependency_map']['reasons'])
        self.assertIn('parse_error_count=2', result['dependency_map']['reasons'])

# このケースで安全側routingとエラー契約が回帰していないことを検証する。
    def test_missing_dependency_map_file_is_explicit_cli_failure(self):
        with tempfile.TemporaryDirectory() as raw:
            missing = Path(raw) / 'missing.json'
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), '--changed', 'src/a.py', '--dependency-map', str(missing)],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, completed.returncode)
            result = json.loads(completed.stdout)
            self.assertEqual('affected-tests', result['tool'])
            self.assertEqual('dependency_map_read_failed', result['status'])


if __name__ == '__main__':
    unittest.main()
