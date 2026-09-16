import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT))

from messenger import discover_policy_files


class PolicyDiscoveryTests(unittest.TestCase):
    def test_discovery_dedupes_overlapping_inputs_and_ignores_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / 'docs'
            docs.mkdir()
            policy = docs / 'policy.md'
            policy.write_text('# Rules\nMust test.\n', encoding='utf-8')
            node = root / 'node_modules' / 'pkg'
            node.mkdir(parents=True)
            (node / 'README.md').write_text('must ignore', encoding='utf-8')

            files, missing, unsupported, errors = discover_policy_files([str(root), str(policy)])
            self.assertEqual([policy], files)
            self.assertEqual([], missing)
            self.assertEqual([], unsupported)
            self.assertEqual(0, errors)

    def test_missing_and_unsupported_inputs_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unsupported = root / 'image.png'
            unsupported.write_bytes(b'x')
            files, missing, unsupported_inputs, errors = discover_policy_files([
                str(root / 'missing.md'),
                str(unsupported),
            ])
            self.assertEqual([], files)
            self.assertEqual([str(root / 'missing.md')], missing)
            self.assertEqual([str(unsupported)], unsupported_inputs)
            self.assertEqual(0, errors)


if __name__ == '__main__':
    unittest.main()
