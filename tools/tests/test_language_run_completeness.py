import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
SCRIPT = TOOLS / 'common/small/language-run/script/language_run.py'
spec = importlib.util.spec_from_file_location('language_run', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LanguageRunCompletenessTests(unittest.TestCase):
    # test_scan_retains_walk_errors は走査不能な領域をclean結果へ丸めないことを確認する。
    def test_scan_retains_walk_errors(self):
        root = Path('project-root')

        def walk(_root, onerror):
            onerror(PermissionError(13, 'denied', str(root / 'restricted')))
            yield str(root), [], ['main.py']

        with mock.patch.object(module.os, 'walk', side_effect=walk):
            languages, errors = module.scan(root)

        self.assertEqual(languages, {'python'})
        self.assertEqual(errors, ['restricted'])

    # test_main_propagates_analyzer_warning はanalyzer warningをstdoutのtop-level statusへ伝える。
    def test_main_propagates_analyzer_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'main.py').write_text('print(1)\n', encoding='utf-8')
            payload = {'tool': 'python-symbols', 'status': 'ok_with_warnings', 'read_error_count': 1, 'files': []}
            completed = subprocess.CompletedProcess([], 0, json.dumps(payload), '')
            output = io.StringIO()
            argv = ['language_run.py', '--acr-root', str(TOOLS.parents[0]), '--out', 'out', str(root)]
            with mock.patch.object(module.shutil, 'which', return_value='python'):
                with mock.patch.object(module.subprocess, 'run', return_value=completed):
                    with mock.patch.object(sys, 'argv', argv):
                        with contextlib.redirect_stdout(output):
                            with self.assertRaises(SystemExit) as exit_result:
                                module.main()
            self.assertEqual(exit_result.exception.code, 0)

            result = json.loads(output.getvalue())
            self.assertEqual(result['status'], 'ok_with_warnings')
            self.assertEqual(result['warning_count'], 1)
            self.assertEqual(result['results'][0]['status'], 'ok_with_warnings')
            self.assertEqual(result['results'][0]['read_error_count'], 1)


if __name__ == '__main__':
    unittest.main()
