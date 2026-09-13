import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).parents[1] / 'script' / 'exploration_stop_check.py'
spec = importlib.util.spec_from_file_location('exploration_stop_check', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ExplorationStopCheckTests(unittest.TestCase):
    def test_ready_when_required_context_is_present(self):
        result = mod.evaluate('Goal Required Acceptance source tests')
        self.assertTrue(result['stop_broad_exploration'])
        self.assertEqual([], result['missing_required_checks'])

    def test_missing_required_context_is_reported(self):
        result = mod.evaluate('Goal source')
        self.assertFalse(result['stop_broad_exploration'])
        self.assertIn('required', result['missing_required_checks'])
        self.assertIn('tests', result['missing_required_checks'])


if __name__ == '__main__':
    unittest.main()
