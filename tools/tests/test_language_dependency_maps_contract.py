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


class LanguageDependencyMapContractTests(unittest.TestCase):
    def test_python_import_map_distinguishes_parse_failure(self):
        script = TOOLS / 'python/medium/python-import-map/script/python_import_map.py'
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'good.py').write_text('import os\n', encoding='utf-8')
            (root / 'broken.py').write_text('def broken(:\n', encoding='utf-8')
            _, result = run_json(script, root)
            self.assertEqual('ok_with_warnings', result['status'])
            self.assertEqual(1, result['parse_error_count'])
            broken = next(row for row in result['files'] if row['file'] == 'broken.py')
            self.assertEqual('parse_failed', broken['status'])
            self.assertEqual([], broken['imports'])

    def test_file_map_limits_only_report_real_truncation(self):
        configs = [
            ('python/medium/python-import-map/script/python_import_map.py', '.py', 'import os\n'),
            ('c/medium/c-include-map/script/c_include_map.py', '.c', '#include <stdio.h>\n'),
            ('cpp/medium/cpp-include-map/script/cpp_include_map.py', '.cpp', '#include <vector>\n'),
            ('gdscript/medium/gdscript-dependency-map/script/gdscript_dependency_map.py', '.gd', 'extends "res://base.gd"\n'),
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
                self.assertEqual(1, limited['files_returned'])

    def test_missing_root_is_not_empty_success(self):
        scripts = [
            TOOLS / 'python/medium/python-import-map/script/python_import_map.py',
            TOOLS / 'c/medium/c-include-map/script/c_include_map.py',
            TOOLS / 'cpp/medium/cpp-include-map/script/cpp_include_map.py',
            TOOLS / 'gdscript/medium/gdscript-dependency-map/script/gdscript_dependency_map.py',
            TOOLS / 'csharp/medium/csharp-project-map/script/csharp_project_map.py',
        ]
        with tempfile.TemporaryDirectory() as raw:
            missing = Path(raw) / 'missing'
            for script in scripts:
                code, result = run_json(script, missing, check=False)
                self.assertNotEqual(0, code, str(script))
                self.assertEqual('input_missing', result['status'], str(script))

    def test_csharp_source_listing_is_bounded_without_losing_total(self):
        script = TOOLS / 'csharp/medium/csharp-project-map/script/csharp_project_map.py'
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'Demo.csproj').write_text('<Project></Project>\n', encoding='utf-8')
            (root / 'A.cs').write_text('class A {}\n', encoding='utf-8')
            (root / 'B.cs').write_text('class B {}\n', encoding='utf-8')
            _, result = run_json(script, '--max-source-files-per-project', '1', root)
            self.assertEqual('ok', result['status'])
            project = result['projects'][0]
            self.assertEqual(2, project['source_file_count_total'])
            self.assertEqual(1, len(project['source_files']))
            self.assertTrue(project['source_files_truncated'])


if __name__ == '__main__':
    unittest.main()
