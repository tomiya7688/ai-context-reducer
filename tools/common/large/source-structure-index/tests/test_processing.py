import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'processing.py'
spec = importlib.util.spec_from_file_location('source_structure_processing', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SourceStructureProcessingTests(unittest.TestCase):
    def test_build_normalizes_symbols_and_dependency_graph(self):
        symbols = [
            ('symbols.json', [
                {
                    'file': 'pkg/a.py',
                    'symbols': [
                        {'kind': 'ClassDef', 'name': 'Service', 'line': 3},
                    ],
                }
            ])
        ]
        graphs = [
            ('graph.json', {
                'edges': [
                    {'from': 'pkg.a', 'to': 'pkg.b'},
                ],
                'truncated': False,
            })
        ]

        index = module.build_index(symbols, graphs)
        node_ids = {row['id'] for row in index['nodes']}
        edge_keys = {(row['from'], row['to'], row['kind']) for row in index['edges']}

        self.assertIn('file:pkg/a.py', node_ids)
        self.assertIn('module:pkg.a', node_ids)
        self.assertIn('symbol:pkg/a.py::Service', node_ids)
        self.assertIn('module:pkg.b', node_ids)
        self.assertIn(('file:pkg/a.py', 'symbol:pkg/a.py::Service', 'owns'), edge_keys)
        self.assertIn(('module:pkg.a', 'module:pkg.b', 'depends_on'), edge_keys)
        self.assertFalse(index['input_truncated'])

    def test_build_preserves_nested_symbol_ownership_and_metadata(self):
        symbols = [
            ('outline.json', {
                'files': [{
                    'file': 'src/service.py',
                    'symbols': [
                        {
                            'kind': 'Class',
                            'name': 'Service',
                            'qualified_name': 'src/service.py::Service',
                            'line': 5,
                            'end_line': 12,
                            'language': 'Python',
                            'signature': 'class Service:',
                        },
                        {
                            'kind': 'Method',
                            'name': 'run',
                            'qualified_name': 'src/service.py::Service::run',
                            'owner_qualified_name': 'src/service.py::Service',
                            'line': 7,
                            'end_line': 9,
                            'language': 'Python',
                            'signature': 'def run(self):',
                        },
                    ],
                }],
                'truncated': False,
            })
        ]
        index = module.build_index(symbols, [])
        edge_keys = {(row['from'], row['to'], row['kind']) for row in index['edges']}
        nodes = {row['id']: row for row in index['nodes']}

        self.assertIn(
            ('symbol:src/service.py::Service', 'symbol:src/service.py::Service::run', 'owns'),
            edge_keys,
        )
        method = nodes['symbol:src/service.py::Service::run']
        self.assertEqual(method['language'], 'Python')
        self.assertEqual(method['signature'], 'def run(self):')
        self.assertEqual(method['owner_qualified_name'], 'src/service.py::Service')

    def test_build_bridges_go_package_to_file(self):
        symbols = [
            ('go-symbols.json', [
                {
                    'file': 'internal/store/store.go',
                    'symbols': [
                        {'kind': 'package', 'name': 'store', 'line': 1},
                        {'kind': 'func', 'name': 'Open', 'line': 8},
                    ],
                }
            ])
        ]
        graphs = [
            ('go-graph.json', {
                'module': 'example.com/project',
                'edges': [],
                'truncated': False,
            })
        ]
        index = module.build_index(symbols, graphs)
        edge_keys = {(row['from'], row['to'], row['kind']) for row in index['edges']}
        self.assertIn(
            ('module:example.com/project/internal/store', 'file:internal/store/store.go', 'contains_file'),
            edge_keys,
        )


    def test_build_propagates_symbol_analyzer_warning_counts(self):
        symbols = [
            ('symbols.json', {
                'tool': 'python-symbols',
                'status': 'ok_with_warnings',
                'files': [
                    {'file': 'pkg/broken.py', 'status': 'parse_failed', 'symbols': []},
                ],
                'parse_error_count': 1,
                'read_error_count': 0,
                'unsupported_input_count': 2,
            })
        ]
        index = module.build_index(symbols, [])
        self.assertEqual(
            ['symbols.json: analyzer warnings parse_error_count=1 unsupported_input_count=2'],
            index['input_errors'],
        )


    def test_query_prefers_exact_name(self):
        index = {
            'nodes': [
                {'id': 'symbol:a::Thing', 'kind': 'symbol', 'name': 'Thing'},
                {'id': 'symbol:b::ThingFactory', 'kind': 'symbol', 'name': 'ThingFactory'},
            ]
        }
        matches, truncated = module.query_nodes(index, 'Thing', 10)
        self.assertEqual('symbol:a::Thing', matches[0]['id'])
        self.assertFalse(truncated)

    def test_expand_is_bounded_and_reports_fan_and_cycles(self):
        index = {
            'nodes': [
                {'id': 'module:a', 'kind': 'module'},
                {'id': 'module:b', 'kind': 'module'},
                {'id': 'module:c', 'kind': 'module'},
            ],
            'edges': [
                {'from': 'module:a', 'to': 'module:b', 'kind': 'depends_on'},
                {'from': 'module:b', 'to': 'module:a', 'kind': 'depends_on'},
                {'from': 'module:b', 'to': 'module:c', 'kind': 'depends_on'},
            ],
        }
        result = module.expand(index, 'module:a', depth=2, max_nodes=2, direction='both')
        ids = {row['id'] for row in result['nodes']}
        self.assertEqual({'module:a', 'module:b'}, ids)
        self.assertTrue(result['nodes_truncated'])
        self.assertEqual([['module:a', 'module:b']], result['cycle_groups'])
        start = next(row for row in result['nodes'] if row['id'] == 'module:a')
        self.assertEqual(1, start['fan_out'])
        self.assertEqual(1, start['fan_in'])


if __name__ == '__main__':
    unittest.main()
