import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'tool_selector.py'
spec = importlib.util.spec_from_file_location('tool_selector', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def paths(rows, key):
    return [row[key] for row in rows]


class ToolSelectorTests(unittest.TestCase):
    def test_recommend_includes_git_tools_with_routing_metadata(self):
        recommended, conditional, recommended_groups, conditional_groups = module.recommend(
            'small', [('python', 3)], [], docs=0, tests=0, has_git=True, external_tools={'rg'}
        )
        self.assertIn('common/medium/compact-diff', paths(recommended, 'tool_path'))
        self.assertIn('common/medium/remote-delta', paths(conditional, 'tool_path'))
        self.assertIn('python/small', paths(recommended_groups, 'tool_group_path'))
        self.assertEqual(conditional_groups, [])
        self.assertTrue(all(row['reason'] and row['phase'] and row['activation'] for row in recommended + conditional))
        search = next(row for row in recommended if row['tool_path'] == 'common/small/text-search')
        self.assertEqual(search['availability'], 'external_backend_ready')

    def test_build_selection_separates_language_and_other_files(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / '.git').mkdir()
            (root / 'main.py').write_text('print(1)\n', encoding='utf-8')
            (root / 'README.md').write_text('# demo\n', encoding='utf-8')
            result = module.build_selection(root)
            self.assertEqual(result['tool'], 'tool-selector')
            self.assertEqual(result['status'], 'ok')
            self.assertTrue(result['git_repository_detected'])
            self.assertEqual(result['language_file_counts'], {'python': 1})
            self.assertEqual(result['recognized_source_files_scanned'], 1)
            self.assertEqual(result['non_language_files_scanned'], 1)
            self.assertFalse(result['scan_truncated'])
            self.assertEqual(result['routing_order'], ['orient', 'search', 'scope', 'inspect', 'validate', 'stop'])
            self.assertFalse(result['task_context']['applied'])
            self.assertTrue(result['exploration_stop_conditions'])

    def test_project_type_detection_uses_relative_path_content(self):
        detected = set()
        module.detect_types_from_relative_path('src/parser/token_stream.py', detected)
        self.assertIn('compiler', detected)
        self.assertNotIn('simulation', detected)

    def test_large_rule_heavy_repo_gets_structure_and_backend_tools(self):
        recommended, conditional, recommended_groups, conditional_groups = module.recommend(
            'large', [('python', 100)], ['rule_heavy'], docs=5, tests=10, has_git=True,
            external_tools={'git-sizer', 'tree-sitter', 'ast-grep'}
        )
        self.assertIn('common/large/context-manifest', paths(recommended, 'tool_path'))
        self.assertIn('common/large/source-structure-index', paths(recommended, 'tool_path'))
        self.assertIn('common/medium/structural-search', paths(conditional, 'tool_path'))
        self.assertIn('common/medium/policy-index', paths(conditional, 'tool_path'))
        self.assertIn('common/small/git-history-health', paths(conditional, 'tool_path'))
        self.assertIn('common/small/syntax-health', paths(conditional, 'tool_path'))
        self.assertIn('python/small', paths(recommended_groups, 'tool_group_path'))
        self.assertIn('python/large', paths(conditional_groups, 'tool_group_path'))
        phases = [module.PHASE_ORDER[row['phase']] for row in recommended]
        self.assertEqual(phases, sorted(phases))

    def test_task_context_narrows_routing_to_directly_relevant_tools(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / '.git').mkdir()
            (root / 'src').mkdir()
            (root / 'src' / 'service.py').write_text('def run():\n    pass\n', encoding='utf-8')
            (root / 'tests').mkdir()
            (root / 'tests' / 'test_service.py').write_text('def test_run():\n    pass\n', encoding='utf-8')
            (root / 'TASK.md').write_text('# Goal\nChange service behavior\n', encoding='utf-8')
            result = module.build_selection(
                root,
                goal='Change service behavior',
                task_file='TASK.md',
                changed_files=['src/service.py'],
                validation_intent='targeted',
            )
            selected = paths(result['recommended_tools'], 'tool_path')
            self.assertTrue(result['task_context']['applied'])
            self.assertEqual(result['conditional_tools'], [])
            self.assertIn('common/small/text-search', selected)
            self.assertIn('common/medium/acceptance-extractor', selected)
            self.assertIn('common/medium/compact-diff', selected)
            self.assertIn('common/medium/change-router', selected)
            self.assertIn('common/medium/validation-plan', selected)
            self.assertNotIn('common/large/context-budget', selected)
            self.assertTrue(all(row['task_relevance'] == 'direct' for row in result['recommended_tools']))
            self.assertGreater(result['task_context']['deferred_tool_count'], 0)

    def test_latest_file_is_not_counted_as_test(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'latest.py').write_text('x = 1\n', encoding='utf-8')
            result = module.build_selection(root)
            self.assertEqual(result['test_file_count'], 0)


if __name__ == '__main__':
    unittest.main()
