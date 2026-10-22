import importlib.util
import json
import platform
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

selection_spec = importlib.util.spec_from_file_location('selection', SCRIPT_DIR / 'selection.py')
selection = importlib.util.module_from_spec(selection_spec)
selection_spec.loader.exec_module(selection)

materialize_spec = importlib.util.spec_from_file_location('materialize_tools', SCRIPT_DIR / 'materialize_tools.py')
materialize = importlib.util.module_from_spec(materialize_spec)
materialize_spec.loader.exec_module(materialize)


class MaterializeToolsTests(unittest.TestCase):
    # {責務: [make_python_source: Pythonツールと両OS用の入口を含む配布原本を作る], 処理: [1: 最小のソースを保存する, 2: 両OSで使う入口を用意する], 引数: [root: 原本の保存先], 戻り値: []}
    def make_python_source(self, root: Path) -> None:
        for relative in selection.PYTHON_TOOL_PATHS:
            path = root / 'tools' / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'# {relative.as_posix()}\n', encoding='utf-8')
        wrapper = root / 'tools' / 'analyze.sh'
        wrapper.parent.mkdir(parents=True, exist_ok=True)
        wrapper.write_text('#!/usr/bin/env sh\n', encoding='utf-8')
        wrapper.with_suffix('.bat').write_text('@echo off\n', encoding='utf-8')

    # test_python_selection_preserves_wrapper_expected_layout は選択Python fileをwrapperが期待する相対pathへ配置することを確認します。
    def test_python_selection_preserves_wrapper_expected_layout(self):
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw)
            self.make_python_source(source)
            mode, rows = selection.choose(source, system='linux', python_executable='/usr/bin/python3')
            destinations = {Path(row['destination']).as_posix() for row in rows}
            self.assertEqual(mode, 'python')
            self.assertIn('analyze.sh', destinations)
            self.assertIn('common/small/analyze-and-recommend/script/analyze_and_recommend.py', destinations)
            self.assertIn('common/small/tool-selector/script/tool_selector.py', destinations)
            self.assertNotIn('analyze_and_recommend.py', destinations)

    # test_native_selection_places_binary_under_bin_for_wrapper はnative executableをbin配下へmaterializeすることを確認します。
    def test_native_selection_places_binary_under_bin_for_wrapper(self):
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw)
            binary = source / 'tools' / 'bin' / 'acr-toolbox'
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'native')
            wrapper = source / 'tools' / 'analyze.sh'
            wrapper.write_text('#!/usr/bin/env sh\n', encoding='utf-8')
            mode, rows = selection.choose(source, system='linux', python_executable='/usr/bin/python3')
            destinations = {Path(row['destination']).as_posix() for row in rows}
            self.assertEqual(mode, 'native')
            self.assertEqual(destinations, {'bin/acr-toolbox', 'analyze.sh'})

    # {責務: [test_preview_apply_manifest_and_conflict_protection: 適用時だけ配置しOSに合う入口と衝突保護を維持することを確認する], 処理: [1: 確認だけの結果を調べる, 2: 適用結果と一覧を確認する, 3: 衝突の拒否と上書きの指定を確認する], 引数: [], 戻り値: []}
    def test_preview_apply_manifest_and_conflict_protection(self):
        with tempfile.TemporaryDirectory() as source_raw, tempfile.TemporaryDirectory() as out_raw:
            source = Path(source_raw)
            out = Path(out_raw)
            self.make_python_source(source)
            wrapper_name = 'analyze.bat' if platform.system().lower() == 'windows' else 'analyze.sh'

            preview = materialize.execute(source, out, apply=False, overwrite=False)
            self.assertEqual(preview['status'], 'ok')
            self.assertFalse(preview['applied'])
            self.assertTrue(all(row['planned_action'] == 'create' for row in preview['actions']))

            applied = materialize.execute(source, out, apply=True, overwrite=False)
            self.assertEqual(applied['status'], 'ok')
            self.assertTrue(applied['applied'])
            self.assertTrue((out / wrapper_name).exists())
            analyzer = out / 'common/small/analyze-and-recommend/script/analyze_and_recommend.py'
            selector = out / 'common/small/tool-selector/script/tool_selector.py'
            self.assertTrue(analyzer.exists())
            self.assertTrue(selector.exists())

            manifest = json.loads((out / materialize.MANIFEST_NAME).read_text(encoding='utf-8'))
            self.assertEqual(manifest['format'], materialize.MANIFEST_FORMAT)
            manifest_paths = {row['path'] for row in manifest['files']}
            self.assertIn(wrapper_name, manifest_paths)
            self.assertIn('common/small/analyze-and-recommend/script/analyze_and_recommend.py', manifest_paths)
            self.assertIn('common/small/tool-selector/script/tool_selector.py', manifest_paths)

            analyzer.write_text('# locally changed\n', encoding='utf-8')
            conflict = materialize.execute(source, out, apply=True, overwrite=False)
            self.assertEqual(conflict['status'], 'conflict')
            self.assertFalse(conflict['applied'])
            self.assertIn('common/small/analyze-and-recommend/script/analyze_and_recommend.py', conflict['conflicting_destination_paths'])
            self.assertEqual(analyzer.read_text(encoding='utf-8'), '# locally changed\n')

            overwrite_preview = materialize.execute(source, out, apply=False, overwrite=True)
            changed_action = next(row for row in overwrite_preview['actions'] if row['destination_path'].endswith('analyze_and_recommend.py'))
            self.assertEqual(changed_action['planned_action'], 'overwrite')

            overwritten = materialize.execute(source, out, apply=True, overwrite=True)
            self.assertEqual(overwritten['status'], 'ok')
            self.assertTrue(overwritten['applied'])
            self.assertNotEqual(analyzer.read_text(encoding='utf-8'), '# locally changed\n')


if __name__ == '__main__':
    unittest.main()
