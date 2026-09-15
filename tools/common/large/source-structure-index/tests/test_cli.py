import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'source_structure_index.py'


class SourceStructureIndexCliTests(unittest.TestCase):
    def test_build_query_expand_affected_round_trip(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            symbols = root / 'symbols.json'
            graph = root / 'graph.json'
            index = root / 'index.json'

            symbols.write_text(json.dumps([
                {
                    'file': 'pkg/a.py',
                    'symbols': [{'kind': 'ClassDef', 'name': 'Service', 'line': 4}],
                },
                {
                    'file': 'pkg/b.py',
                    'symbols': [{'kind': 'FunctionDef', 'name': 'load', 'line': 2}],
                },
            ]), encoding='utf-8')
            graph.write_text(json.dumps({
                'edges': [{'from': 'pkg.a', 'to': 'pkg.b'}],
                'truncated': False,
            }), encoding='utf-8')

            built = subprocess.run(
                [
                    sys.executable, str(SCRIPT), 'build',
                    '--symbols', str(symbols),
                    '--graph', str(graph),
                    '--output', str(index),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, built.returncode, built.stderr)
            build_result = json.loads(built.stdout)
            self.assertEqual('ok', build_result['status'])
            self.assertTrue(index.exists())
            self.assertNotIn('nodes', build_result)

            queried = subprocess.run(
                [sys.executable, str(SCRIPT), 'query', str(index), 'Service'],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, queried.returncode, queried.stderr)
            query_result = json.loads(queried.stdout)
            self.assertEqual('symbol:pkg/a.py::Service', query_result['matches'][0]['id'])

            expanded = subprocess.run(
                [sys.executable, str(SCRIPT), 'expand', str(index), 'module:pkg.a', '--depth', '1'],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, expanded.returncode, expanded.stderr)
            expand_result = json.loads(expanded.stdout)
            self.assertEqual('ok', expand_result['status'])
            node_ids = {row['id'] for row in expand_result['nodes']}
            self.assertIn('module:pkg.b', node_ids)
            self.assertIn('file:pkg/a.py', node_ids)

            affected = subprocess.run(
                [
                    sys.executable, str(SCRIPT), 'affected', str(index),
                    '--changed', 'pkg/b.py',
                    '--max-results', '80',
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, affected.returncode, affected.stderr)
            affected_result = json.loads(affected.stdout)
            self.assertEqual('ok', affected_result['status'])
            affected_ids = [row['id'] for row in affected_result['affected_modules']]
            self.assertEqual(['module:pkg.b', 'module:pkg.a'], affected_ids)
            self.assertEqual('targeted_dependents', affected_result['recommended_validation_scope'])

    def test_build_accepts_ast_grep_outline_shape(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            outline = root / 'outline.json'
            index = root / 'index.json'
            outline.write_text(json.dumps([{
                'path': 'src/service.py',
                'language': 'Python',
                'items': [{
                    'name': 'Service',
                    'symbolType': 'Class',
                    'range': {'start': {'line': 1}, 'end': {'line': 5}},
                    'members': [{
                        'name': 'run',
                        'symbolType': 'Method',
                        'range': {'start': {'line': 2}, 'end': {'line': 3}},
                        'members': [],
                    }],
                }],
            }]), encoding='utf-8')

            built = subprocess.run(
                [
                    sys.executable, str(SCRIPT), 'build',
                    '--symbols', str(outline),
                    '--output', str(index),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, built.returncode, built.stderr)
            query = subprocess.run(
                [sys.executable, str(SCRIPT), 'query', str(index), 'run'],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, query.returncode, query.stderr)
            result = json.loads(query.stdout)
            self.assertEqual('symbol:src/service.py::Service::run', result['matches'][0]['id'])
            self.assertEqual('src/service.py::Service', result['matches'][0]['owner_qualified_name'])


if __name__ == '__main__':
    unittest.main()
