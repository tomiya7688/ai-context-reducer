import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'tools' / 'common'
CLI_RELATIVE_PATHS = {
    'analyze-and-recommend': 'small/analyze-and-recommend/script/analyze_and_recommend.py',
    'tree-view': 'small/tree-view/script/tree_view.py',
    'doc-index': 'small/doc-index/script/doc_index.py',
    'file-role-map': 'small/file-role-map/script/file_role_map.py',
    'tool-selector': 'small/tool-selector/script/tool_selector.py',
    'source-of-truth-candidates': 'small/source-of-truth-candidates/script/source_of_truth_candidates.py',
    'context-budget': 'large/context-budget/script/context_budget.py',
    'hotspot-report': 'large/hotspot-report/script/hotspot_report.py',
    'structural-search': 'medium/structural-search/script/structural_search.py',
    'compact-diff': 'medium/compact-diff/script/compact_diff.py',
    'remote-delta': 'medium/remote-delta/script/remote_delta.py',
}


class PythonCliExitPolicyTests(unittest.TestCase):
    def run_cli(self, name, *arguments, cwd=None, env=None):
        script = TOOLS / CLI_RELATIVE_PATHS[name]
        completed = subprocess.run(
            [sys.executable, str(script), *map(str, arguments)],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(completed.stdout) if completed.stdout.strip() else None
        return completed, payload

    def test_all_clis_return_nonzero_for_missing_input_root(self):
        missing = ROOT / 'tools' / 'common' / '__issue45_missing_fixture__'
        for name in CLI_RELATIVE_PATHS:
            with self.subTest(cli=name):
                args = ['print($ARG)'] if name == 'structural-search' else []
                if name == 'compact-diff':
                    args.extend(['--base', 'missing-ref', '--head', 'HEAD'])
                else:
                    args.append(missing)
                completed, payload = self.run_cli(name, *args, cwd=ROOT)
                self.assertEqual(completed.returncode, 2)
                self.assertIsNotNone(payload)
                self.assertIn(payload['status'], {
                    'input_missing', 'git_unavailable', 'git_unavailable_or_not_repository', 'git_query_failed',
                })

    def test_policy_documents_every_tested_user_facing_cli(self):
        policy = (ROOT / 'tools' / 'PYTHON_CLI_EXIT_POLICY.md').read_text(encoding='utf-8')
        for name in CLI_RELATIVE_PATHS:
            with self.subTest(cli=name):
                self.assertIn(f'| {name} |', policy)

    def test_normal_analysis_and_optional_unavailable_statuses_return_zero(self):
        root = ROOT / 'tools' / 'common' / 'tests'
        cases = {
            'analyze-and-recommend': (root,),
            'tree-view': (root,),
            'doc-index': (root,),
            'file-role-map': (root,),
            'tool-selector': (root,),
            'source-of-truth-candidates': (root,),
            'context-budget': (root,),
            'hotspot-report': (root,),
            'structural-search': ('print($ARG)', root, '--backend', 'fallback'),
            'compact-diff': ('--base', 'HEAD', '--head', 'HEAD'),
            'remote-delta': (ROOT, '--remote', 'issue45/nonexistent-remote'),
        }
        for name, args in cases.items():
            with self.subTest(cli=name):
                completed, payload = self.run_cli(name, *args, cwd=ROOT)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertIn(payload['status'], {'ok', 'ok_with_warnings', 'remote_unavailable'})

    def test_structural_search_rejects_invalid_query_with_nonzero_exit(self):
        root = ROOT / 'tools' / 'common' / 'tests'
        completed, payload = self.run_cli(
            'structural-search', '$$$ARGS', root, '--backend', 'fallback'
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(payload['status'], 'invalid_pattern')

    def test_optional_structural_backends_return_zero_with_explicit_status(self):
        root = ROOT / 'tools' / 'common' / 'tests'
        with tempfile.TemporaryDirectory(prefix='.tmp-no-tools-', dir=ROOT) as empty_path:
            env = os.environ.copy()
            env['PATH'] = empty_path
            for args, expected_status in (
                (('print($ARG)', root, '--backend', 'ast-grep'), 'backend_unavailable'),
                (('print($ARG)', root, '--lang', 'c', '--backend', 'fallback'), 'backend_unavailable_for_language'),
            ):
                with self.subTest(status=expected_status):
                    completed, payload = self.run_cli('structural-search', *args, cwd=root, env=env)
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertEqual(payload['status'], expected_status)

    def test_negative_limit_is_rejected(self):
        root = ROOT / 'tools' / 'common' / 'tests'
        completed, payload = self.run_cli('tree-view', root, '--max-entries', '-1')
        self.assertEqual(completed.returncode, 2)
        self.assertIsNone(payload)
        self.assertIn('must be non-negative', completed.stderr)


if __name__ == '__main__':
    unittest.main()
