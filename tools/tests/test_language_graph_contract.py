import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]


def run_json(script, *args, check=True):
    completed = subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        text=True,
        capture_output=True,
        check=check,
    )
    return completed.returncode, json.loads(completed.stdout)


class LanguageGraphContractTests(unittest.TestCase):
    def test_python_module_graph_reports_parse_failure(self):
        script = TOOLS / 'python/large/python-module-graph/script/python_module_graph.py'
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'good.py').write_text('import os\n', encoding='utf-8')
            (root / 'broken.py').write_text('def broken(:\n', encoding='utf-8')
            _, result = run_json(script, root)
            self.assertEqual('ok_with_warnings', result['status'])
            self.assertEqual(1, result['parse_error_count'])
            self.assertEqual(2, result['files_scanned'])
            self.assertFalse(result['scan_truncated'])

    def test_graph_limits_only_report_real_truncation(self):
        configs = [
            ('python/large/python-module-graph/script/python_module_graph.py', '.py', 'x = 1\n'),
            ('c/large/c-include-graph/script/c_include_graph.py', '.c', 'int main(void) { return 0; }\n'),
            ('cpp/large/cpp-include-graph/script/cpp_include_graph.py', '.cpp', 'int main() { return 0; }\n'),
        ]
        for relative, suffix, content in configs:
            script = TOOLS / relative
            with tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                (root / f'a{suffix}').write_text(content, encoding='utf-8')
                _, exact = run_json(script, '--limit', '1', root)
                self.assertFalse(exact['scan_truncated'], relative)
                (root / f'b{suffix}').write_text(content, encoding='utf-8')
                _, limited = run_json(script, '--limit', '1', root)
                self.assertTrue(limited['scan_truncated'], relative)
                self.assertEqual(2, limited['file_count_total'])
                self.assertEqual(1, limited['files_scanned'])

    def test_godot_scene_graph_keeps_total_when_bounded(self):
        script = TOOLS / 'gdscript/large/godot-scene-graph/script/godot_scene_graph.py'
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'a.tscn').write_text('[node name="A" type="Node"]\n', encoding='utf-8')
            (root / 'b.tscn').write_text('[node name="B" type="Node"]\n', encoding='utf-8')
            _, result = run_json(script, '--limit', '1', root)
            self.assertTrue(result['scan_truncated'])
            self.assertEqual(2, result['scene_count_total'])
            self.assertEqual(1, result['scenes_returned'])

    def test_missing_root_is_not_empty_graph(self):
        scripts = [
            TOOLS / 'python/large/python-module-graph/script/python_module_graph.py',
            TOOLS / 'c/large/c-include-graph/script/c_include_graph.py',
            TOOLS / 'cpp/large/cpp-include-graph/script/cpp_include_graph.py',
            TOOLS / 'csharp/large/csharp-project-graph/script/csharp_project_graph.py',
            TOOLS / 'gdscript/large/godot-scene-graph/script/godot_scene_graph.py',
        ]
        with tempfile.TemporaryDirectory() as raw:
            missing = Path(raw) / 'missing'
            for script in scripts:
                code, result = run_json(script, missing, check=False)
                self.assertNotEqual(0, code, str(script))
                self.assertEqual('input_missing', result['status'], str(script))


if __name__ == '__main__':
    unittest.main()
