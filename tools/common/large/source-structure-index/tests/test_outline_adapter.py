import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'outline_adapter.py'
spec = importlib.util.spec_from_file_location('source_structure_outline_adapter', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class OutlineAdapterTests(unittest.TestCase):
    def test_detects_and_flattens_nested_outline(self):
        payload = [{
            'path': 'src/service.py',
            'language': 'Python',
            'items': [{
                'name': 'Service',
                'symbolType': 'Class',
                'signature': 'class Service:',
                'range': {
                    'start': {'line': 4, 'column': 0},
                    'end': {'line': 12, 'column': 0},
                },
                'members': [{
                    'name': 'run',
                    'symbolType': 'Method',
                    'signature': 'def run(self):',
                    'range': {
                        'start': {'line': 6, 'column': 4},
                        'end': {'line': 8, 'column': 8},
                    },
                    'members': [],
                }],
            }],
        }]

        self.assertTrue(module.is_ast_grep_outline(payload))
        result = module.normalize_symbol_payload(payload)
        self.assertEqual(result['input_adapter'], 'ast-grep-outline')
        self.assertFalse(result['truncated'])
        symbols = result['files'][0]['symbols']
        self.assertEqual(symbols[0]['qualified_name'], 'src/service.py::Service')
        self.assertEqual(symbols[0]['line'], 5)
        self.assertEqual(symbols[1]['qualified_name'], 'src/service.py::Service::run')
        self.assertEqual(symbols[1]['owner_qualified_name'], 'src/service.py::Service')
        self.assertEqual(symbols[1]['line'], 7)

    def test_existing_symbol_payload_is_unchanged(self):
        payload = [{'file': 'a.py', 'symbols': [{'name': 'A', 'kind': 'ClassDef', 'line': 1}]}]
        self.assertFalse(module.is_ast_grep_outline(payload))
        self.assertIs(module.normalize_symbol_payload(payload), payload)

    def test_signature_is_bounded(self):
        payload = [{
            'path': 'src/a.py',
            'items': [{
                'name': 'A',
                'signature': 'x' * 300,
                'range': {'start': {'line': 0}, 'end': {'line': 0}},
                'members': [],
            }],
        }]
        result = module.normalize_symbol_payload(payload)
        self.assertEqual(len(result['files'][0]['symbols'][0]['signature']), module.SIGNATURE_LIMIT)


if __name__ == '__main__':
    unittest.main()
