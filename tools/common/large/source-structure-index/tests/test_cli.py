import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'source_structure_index.py'


class SourceStructureIndexCliTests(unittest.TestCase):
    def test_build_query_expand_round_trip(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            symbols = root / 'symbols.json'
            graph = root / 'graph.json'
            index = root / 'index.json'

            symbols.write_text(json.dumps([
                {
                    'file': 'pkg/a.py',
                    'symbols': [{'kind': 'ClassDef', 'name': 'Service', 'line': 4}],
                }
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


if __name__ == '__main__':
    unittest.main()
