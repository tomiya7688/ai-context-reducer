import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from ctags_adapter import normalize_ctags_rows
from messenger import ctags_json
from processing import build_index


class CtagsAdapterTests(unittest.TestCase):
    # 複数ctags kind/scopeを含むfixtureを共通化し、正規化境界を同条件で検証する。
    def sample_rows(self):
        return [
            {'_type': 'ptag', 'name': 'JSON_OUTPUT_VERSION', 'path': '1.0'},
            {'_type': 'tag', 'name': 'Klass', 'path': 'src/app.py', 'line': 1, 'language': 'Python', 'kind': 'class'},
            {
                '_type': 'tag', 'name': 'method', 'path': 'src/app.py', 'line': 3,
                'language': 'Python', 'kind': 'member', 'scope': 'Klass',
                'scopeKind': 'class', 'signature': '(self)',
            },
        ]

    # test_scope_becomes_symbol_ownershipでsource-structureのrouting・完全性・bounded出力契約を回帰検証する。
    def test_scope_becomes_symbol_ownership(self):
        payload, metadata = normalize_ctags_rows(self.sample_rows())
        self.assertEqual(metadata['tag_count'], 2)
        self.assertEqual(metadata['file_count'], 1)
        self.assertEqual(metadata['languages'], ['Python'])

        index = build_index([('ctags', payload)], [], None)
        nodes = {node['id']: node for node in index['nodes']}
        self.assertIn('symbol:src/app.py::Klass', nodes)
        self.assertEqual(nodes['symbol:src/app.py::Klass::method']['owner_qualified_name'], 'src/app.py::Klass')
        self.assertIn(
            {'from': 'symbol:src/app.py::Klass', 'to': 'symbol:src/app.py::Klass::method', 'kind': 'owns'},
            index['edges'],
        )

    # test_missing_ctags_backend_is_explicitでsource-structureのrouting・完全性・bounded出力契約を回帰検証する。
    def test_missing_ctags_backend_is_explicit(self):
        with mock.patch('messenger.shutil.which', return_value=None):
            result = ctags_json('src')
        self.assertFalse(result['ok'])
        self.assertEqual(result['status'], 'backend_unavailable')
        self.assertEqual(result['backend'], 'ctags')

    # test_cli_accepts_existing_ctags_json_linesでsource-structureのrouting・完全性・bounded出力契約を回帰検証する。
    def test_cli_accepts_existing_ctags_json_lines(self):
        script = SCRIPT_DIR / 'source_structure_index.py'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'tags.jsonl'
            source.write_text('\n'.join(json.dumps(row) for row in self.sample_rows()) + '\n', encoding='utf-8')
            output = root / 'index.json'
            run = subprocess.run(
                [sys.executable, str(script), 'build', '--ctags-json', str(source), '--output', str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            summary = json.loads(run.stdout)
            self.assertEqual(summary['status'], 'ok')
            self.assertEqual(summary['ctags_inputs'][0]['tag_count'], 2)
            index = json.loads(output.read_text(encoding='utf-8'))
            self.assertTrue(any(node.get('qualified_name') == 'src/app.py::Klass::method' for node in index['nodes']))


if __name__ == '__main__':
    unittest.main()
