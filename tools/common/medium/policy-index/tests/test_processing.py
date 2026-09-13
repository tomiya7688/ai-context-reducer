import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT))

from processing import policy_findings


class PolicyFindingsTest(unittest.TestCase):
    def test_rule_line_has_heading(self):
        findings = list(policy_findings(['# Rules', 'required: targeted tests', 'note']))
        self.assertEqual(findings[0][0], 2)
        self.assertEqual(findings[0][1], 'Rules')


if __name__ == '__main__':
    unittest.main()
