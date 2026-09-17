import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = [
    ('python-symbols', 'python', REPO / 'python/small/python-symbols/script/python_symbols.py', '.py', 'def run():\n    pass\n'),
    ('c-symbols', 'c', REPO / 'c/small/c-symbols/script/c_symbols.py', '.c', 'int run(void) {\n  return 0;\n}\n'),
    ('cpp-symbols', 'cpp', REPO / 'cpp/small/cpp-symbols/script/cpp_symbols.py', '.cpp', 'int run() {\n  return 0;\n}\n'),
    ('csharp-symbols', 'csharp', REPO / 'csharp/small/csharp-symbols/script/csharp_symbols.py', '.cs', 'public class Demo {\n  public void Run() {}\n}\n'),
    ('gdscript-symbols', 'gdscript', REPO / 'gdscript/small/gdscript-symbols/script/gdscript_symbols.py', '.gd', 'func run():\n    pass\n'),
]


class LanguageSymbolContractTests(unittest.TestCase):
    def run_tool(self, script, *paths):
        completed = subprocess.run(
            [sys.executable, str(script), *map(str, paths)],
            check=True,
            text=True,
            capture_output=True,
        )
        return json.loads(completed.stdout)

    def test_symbol_tools_share_self_describing_contract(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for tool, language, script, suffix, source in TOOLS:
                path = root / f'sample{suffix}'
                path.write_text(source, encoding='utf-8')
                result = self.run_tool(script, path)
                self.assertEqual(tool, result['tool'])
                self.assertEqual(language, result['language'])
                self.assertEqual('ok', result['status'])
                self.assertEqual(1, result['file_count'])
                self.assertGreaterEqual(result['symbol_count'], 1)
                self.assertEqual('ok', result['files'][0]['status'])
                self.assertEqual(0, result['parse_error_count'])
                self.assertEqual(0, result['read_error_count'])
                self.assertEqual(0, result['unsupported_input_count'])

    def test_unsupported_input_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            unsupported = root / 'notes.txt'
            unsupported.write_text('hello\n', encoding='utf-8')
            for tool, _, script, _, _ in TOOLS:
                result = self.run_tool(script, unsupported)
                self.assertEqual(tool, result['tool'])
                self.assertEqual('ok_with_warnings', result['status'])
                self.assertEqual(1, result['unsupported_input_count'])
                self.assertEqual('unsupported_input', result['unsupported_inputs'][0]['reason'])

    def test_python_parse_failure_is_distinct_from_empty_symbols(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / 'broken.py'
            path.write_text('def broken(:\n', encoding='utf-8')
            result = self.run_tool(TOOLS[0][2], path)
            self.assertEqual('ok_with_warnings', result['status'])
            self.assertEqual(1, result['parse_error_count'])
            self.assertEqual('parse_failed', result['files'][0]['status'])
            self.assertEqual([], result['files'][0]['symbols'])


if __name__ == '__main__':
    unittest.main()
