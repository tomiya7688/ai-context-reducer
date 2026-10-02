import json
import importlib.util
import shutil
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
    def test_python_affected_tests_marks_unavailable_parse_check_incomplete(self):
        script = TOOLS / 'python/medium/affected-tests/script/affected_tests.py'
        spec = importlib.util.spec_from_file_location('affected_tests', script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        state = module.dependency_state({
            'files': [],
            'parse_error_count': None,
            'parse_check_available': False,
        }, True)
        self.assertFalse(state['complete'])
        self.assertIn('dependency_map_parse_check_unavailable', state['reasons'])

    def test_native_maps_match_python_analyzer_contracts_on_same_fixture(self):
        go = shutil.which('go')
        if not go:
            self.skipTest('Go toolchain is required to build acr-toolbox')
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            root = temp / 'fixture'
            out = temp / 'maps'
            root.mkdir()
            fixtures = {
                'src/sample.py': 'import os\nfrom pkg.sub import value\n',
                'src/sample.go': 'package sample\nimport (\n"fmt"\n"strings"\n)\n',
                'src/sample.c': '#include <stdio.h>\n',
                'src/sample.cpp': '#include "widget.hpp"\n',
                'src/sample.gd': 'extends "res://base.gd"\nvar x = preload("res://x.tscn")\n',
                'src/Demo.csproj': '<Project><ItemGroup><ProjectReference Include="../lib/lib.csproj" /></ItemGroup></Project>\n',
                'src/Program.cs': 'class Program {}\n',
            }
            for relative, content in fixtures.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')

            native = temp / ('acr-toolbox.exe' if sys.platform == 'win32' else 'acr-toolbox')
            subprocess.run(
                [go, 'build', '-o', str(native), '.'],
                cwd=TOOLS / 'common/native/acr-toolbox', check=True,
                text=True, capture_output=True,
            )
            subprocess.run([str(native), 'language-medium-run', '--out', str(out), str(root)], check=True, text=True, capture_output=True)

            configs = [
                ('python', 'python/medium/python-import-map/script/python_import_map.py', 'tools_python_medium_python_import_map.json', 'files', 'imports', 'imports_returned'),
                ('go', 'go/medium/go-import-map/main.go', 'tools_go_medium_go_import_map.json', 'files', 'imports', 'imports_returned'),
                ('c', 'c/medium/c-include-map/script/c_include_map.py', 'tools_c_medium_c_include_map.json', 'files', 'includes', 'includes_returned'),
                ('cpp', 'cpp/medium/cpp-include-map/script/cpp_include_map.py', 'tools_cpp_medium_cpp_include_map.json', 'files', 'includes', 'includes_returned'),
                ('gdscript', 'gdscript/medium/gdscript-dependency-map/script/gdscript_dependency_map.py', 'tools_gdscript_medium_gdscript_dependency_map.json', 'files', 'dependencies', 'dependencies_returned'),
            ]
            for language, script, filename, collection, row_key, count_key in configs:
                with self.subTest(language=language):
                    if language == 'go':
                        completed = subprocess.run([go, 'run', str(TOOLS / script), str(root)], check=True, text=True, capture_output=True)
                        python_result = json.loads(completed.stdout)
                    else:
                        _, python_result = run_json(TOOLS / script, root)
                    native_result = json.loads((out / filename).read_text(encoding='utf-8'))
                    native_rows = {row['file']: row[row_key] for row in native_result[collection]}
                    python_rows = {row['file']: row[row_key] for row in python_result[collection]}
                    self.assertEqual(python_rows, native_rows)
                    self.assertEqual(python_result['file_count_total'], native_result['file_count_total'])
                    self.assertEqual(python_result[count_key], native_result[count_key])
                    self.assertEqual(python_result['scan_truncated'], native_result['scan_truncated'])
                    if language == 'python':
                        self.assertIsNone(native_result['parse_error_count'])
                        self.assertFalse(native_result['parse_check_available'])
                    else:
                        self.assertEqual(python_result.get('parse_error_count', 0), native_result.get('parse_error_count', 0))

            csharp_script = TOOLS / 'csharp/medium/csharp-project-map/script/csharp_project_map.py'
            _, python_csharp = run_json(csharp_script, root)
            native_csharp = json.loads((out / 'tools_csharp_medium_csharp_project_map.json').read_text(encoding='utf-8'))
            self.assertEqual(python_csharp['project_count'], native_csharp['project_count'])
            for native_project, python_project in zip(native_csharp['projects'], python_csharp['projects']):
                for key in ('project', 'status', 'project_references', 'source_files', 'source_file_count_total', 'source_files_truncated'):
                    self.assertEqual(python_project[key], native_project[key], key)

    def test_affected_tests_consumes_native_python_map_and_marks_unknown_parse_state(self):
        go = shutil.which('go')
        if not go:
            self.skipTest('Go toolchain is required to build native tools')
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            root = temp / 'fixture'
            out = temp / 'maps'
            root.mkdir()
            (root / 'src').mkdir()
            (root / 'tests').mkdir()
            (root / 'src/pkg.py').write_text('value = 1\n', encoding='utf-8')
            (root / 'src/consumer.py').write_text('from pkg import value\n', encoding='utf-8')
            native = temp / ('acr-toolbox.exe' if sys.platform == 'win32' else 'acr-toolbox')
            affected = temp / ('affected-tests.exe' if sys.platform == 'win32' else 'affected-tests')
            subprocess.run([go, 'build', '-o', str(native), '.'], cwd=TOOLS / 'common/native/acr-toolbox', check=True, text=True, capture_output=True)
            subprocess.run([str(native), 'language-medium-run', '--out', str(out), str(root)], check=True, text=True, capture_output=True)
            subprocess.run([go, 'build', '-o', str(affected), '.'], cwd=TOOLS / 'go/medium/affected-tests', check=True, text=True, capture_output=True)
            dependency_map = out / 'tools_python_medium_python_import_map.json'
            completed = subprocess.run(
                [str(affected), '--root', str(root), '--changed', 'src/pkg.py', '--dependency-map', str(dependency_map)],
                check=True, text=True, capture_output=True,
            )
            result = json.loads(completed.stdout)
            self.assertIn('tests/test_consumer.py', result['test_candidates'])
            self.assertTrue(result['impact_uncertain'])
            self.assertIn('dependency_map_parse_check_unavailable', result['dependency_map']['reasons'])

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
