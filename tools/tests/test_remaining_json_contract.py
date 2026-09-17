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


class RemainingJsonContractTests(unittest.TestCase):
    def test_environment_plan_is_json_without_flag(self):
        script = TOOLS / 'common/small/environment-plan/script/environment_plan.py'
        _, result = run_json(script, TOOLS.parent)
        self.assertEqual('environment-plan', result['tool'])
        self.assertEqual('ok', result['status'])
        self.assertIn('environment', result)
        self.assertIn('plan', result)

    def test_external_tool_probe_is_json_and_has_no_semgrep(self):
        script = TOOLS / 'common/small/external-tool-probe/script/external_tool_probe.py'
        _, result = run_json(script)
        self.assertEqual('external-tool-probe', result['tool'])
        self.assertEqual('ok', result['status'])
        names = {row['name'] for row in result['external_tools']}
        self.assertIn('scip', names)
        self.assertNotIn('semgrep', names)

    def test_architecture_router_is_json_and_reports_missing_profile(self):
        script = TOOLS / 'common/medium/architecture-boundary-router/script/architecture_boundary_router.py'
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            profile = root / 'profile.json'
            profile.write_text(json.dumps({
                'name': 'demo',
                'layers': [{'name': 'data', 'patterns': ['src/data/**']}],
                'roles': [{'name': 'boundary', 'patterns': ['src/data/api.py']}],
                'boundary_roles': ['boundary'],
            }), encoding='utf-8')
            _, result = run_json(script, '--profile', profile, 'src/data/api.py')
            self.assertEqual('architecture-boundary-router', result['tool'])
            self.assertEqual('ok', result['status'])
            self.assertEqual(1, result['route_count'])
            self.assertTrue(result['routes'][0]['boundary'])

            code, failed = run_json(
                script,
                '--profile',
                root / 'missing.json',
                'src/data/api.py',
                check=False,
            )
            self.assertNotEqual(0, code)
            self.assertEqual('profile_missing', failed['status'])


if __name__ == '__main__':
    unittest.main()
