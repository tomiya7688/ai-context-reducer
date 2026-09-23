import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from scip_adapter import normalize_scip_print


class ScipAdapterTests(unittest.TestCase):
    # test_symbols_ownership_locations_and_dependenciesでadapter正規化・graph構築・失敗境界の契約が回帰していないことを検証する。
    def test_symbols_ownership_locations_and_dependencies(self):
        payload = {
            'metadata': {
                'projectRoot': 'file:///repo',
                'toolInfo': {'name': 'scip-test', 'version': '1.0'},
            },
            'documents': [
                {
                    'relativePath': 'pkg/a.py',
                    'language': 'Python',
                    'symbols': [
                        {
                            'symbol': 'scip-python python pkg 1.0 A#',
                            'displayName': 'A',
                            'kind': 'Class',
                        },
                        {
                            'symbol': 'scip-python python pkg 1.0 A#do().',
                            'displayName': 'do',
                            'kind': 'Method',
                            'enclosingSymbol': 'scip-python python pkg 1.0 A#',
                            'signatureDocumentation': {'language': 'python', 'text': 'def do(self) -> B'},
                        },
                    ],
                    'occurrences': [
                        {
                            'range': [0, 0, 1],
                            'symbol': 'scip-python python pkg 1.0 A#',
                            'symbolRoles': 1,
                        },
                        {
                            'range': [2, 4, 6],
                            'symbol': 'scip-python python pkg 1.0 B#',
                            'symbolRoles': 8,
                        },
                    ],
                },
                {
                    'relativePath': 'pkg/b.py',
                    'language': 'Python',
                    'symbols': [
                        {
                            'symbol': 'scip-python python pkg 1.0 B#',
                            'displayName': 'B',
                            'kind': 'Class',
                        },
                    ],
                    'occurrences': [
                        {
                            'range': [4, 0, 1],
                            'symbol': 'scip-python python pkg 1.0 B#',
                            'symbolRoles': 1,
                        },
                    ],
                },
            ],
        }

        symbols, graph, metadata = normalize_scip_print(payload)
        by_file = {row['file']: row for row in symbols}
        a_symbols = {row['name']: row for row in by_file['pkg/a.py']['symbols']}
        b_symbols = {row['name']: row for row in by_file['pkg/b.py']['symbols']}

        self.assertEqual(1, a_symbols['A']['line'])
        self.assertEqual(5, b_symbols['B']['line'])
        self.assertEqual('scip-python python pkg 1.0 A#', a_symbols['do']['owner_qualified_name'])
        self.assertEqual('def do(self) -> B', a_symbols['do']['signature'])

        edge_keys = {(row['from'], row['to'], row['kind']) for row in graph['edges']}
        self.assertIn(
            ('module:scip:pkg/a.py', 'module:scip:pkg/b.py', 'depends_on'),
            edge_keys,
        )
        self.assertIn(
            ('module:scip:pkg/a.py', 'file:pkg/a.py', 'contains_file'),
            edge_keys,
        )
        self.assertEqual(2, metadata['document_count'])
        self.assertEqual('scip-test', metadata['indexer']['name'])

    # test_rejects_non_scip_shapeでadapter正規化・graph構築・失敗境界の契約が回帰していないことを検証する。
    def test_rejects_non_scip_shape(self):
        with self.assertRaises(ValueError):
            normalize_scip_print({'files': []})


if __name__ == '__main__':
    unittest.main()
