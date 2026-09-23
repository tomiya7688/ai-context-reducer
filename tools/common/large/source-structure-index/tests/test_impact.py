import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'impact.py'
spec = importlib.util.spec_from_file_location('source_structure_impact', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ImpactTests(unittest.TestCase):
    # 依存・逆依存・truncationを含む最小graph fixtureを作り、impact判定を分離検証する。
    def index(self):
        return {
            'format': 'acr-source-structure-index-v1',
            'input_truncated': False,
            'nodes': [
                {'id': 'module:a', 'kind': 'module', 'name': 'a'},
                {'id': 'module:b', 'kind': 'module', 'name': 'b'},
                {'id': 'module:c', 'kind': 'module', 'name': 'c'},
                {'id': 'file:a.py', 'kind': 'file', 'path': 'a.py'},
                {'id': 'file:b.py', 'kind': 'file', 'path': 'b.py'},
                {'id': 'file:c.py', 'kind': 'file', 'path': 'c.py'},
            ],
            'edges': [
                {'from': 'module:a', 'to': 'file:a.py', 'kind': 'contains_file'},
                {'from': 'module:b', 'to': 'file:b.py', 'kind': 'contains_file'},
                {'from': 'module:c', 'to': 'file:c.py', 'kind': 'contains_file'},
                {'from': 'module:a', 'to': 'module:b', 'kind': 'depends_on'},
                {'from': 'module:c', 'to': 'module:a', 'kind': 'depends_on'},
            ],
        }

    # test_changed_dependency_finds_transitive_dependentsでsource-structureのrouting・完全性・bounded出力契約を回帰検証する。
    def test_changed_dependency_finds_transitive_dependents(self):
        result = module.affected_scope(self.index(), ['b.py'], 80)
        ids = [row['id'] for row in result['affected_modules']]
        distances = {row['id']: row['distance_from_change'] for row in result['affected_modules']}
        self.assertEqual(ids, ['module:b', 'module:a', 'module:c'])
        self.assertEqual(distances['module:b'], 0)
        self.assertEqual(distances['module:a'], 1)
        self.assertEqual(distances['module:c'], 2)
        self.assertFalse(result['impact_uncertain'])
        self.assertEqual(result['recommended_validation_scope'], 'targeted_dependents')

    # test_output_limit_does_not_change_total_closureでsource-structureのrouting・完全性・bounded出力契約を回帰検証する。
    def test_output_limit_does_not_change_total_closure(self):
        result = module.affected_scope(self.index(), ['b.py'], 2)
        self.assertEqual(result['affected_module_count_total'], 3)
        self.assertEqual(result['affected_modules_returned'], 2)
        self.assertTrue(result['affected_modules_truncated'])
        self.assertTrue(result['impact_uncertain'])
        self.assertIn('affected_module_output_was_truncated', result['uncertainty_reasons'])
        self.assertEqual(result['recommended_validation_scope'], 'broader_or_full')

    # test_unmatched_changed_file_forces_broader_scopeでsource-structureのrouting・完全性・bounded出力契約を回帰検証する。
    def test_unmatched_changed_file_forces_broader_scope(self):
        result = module.affected_scope(self.index(), ['missing.py'], 80)
        self.assertEqual(result['unmatched_changed_files'], ['missing.py'])
        self.assertTrue(result['impact_uncertain'])
        self.assertEqual(result['affected_module_count_total'], 0)
        self.assertEqual(result['recommended_validation_scope'], 'broader_or_full')

    # test_truncated_index_is_never_reported_as_certainでsource-structureのrouting・完全性・bounded出力契約を回帰検証する。
    def test_truncated_index_is_never_reported_as_certain(self):
        index = self.index()
        index['input_truncated'] = True
        result = module.affected_scope(index, ['b.py'], 80)
        self.assertTrue(result['impact_uncertain'])
        self.assertIn('source_structure_index_input_was_truncated', result['uncertainty_reasons'])


if __name__ == '__main__':
    unittest.main()
