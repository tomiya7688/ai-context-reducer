import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from messenger import scip_print_json


class ScipMessengerTests(unittest.TestCase):
    # test_missing_scip_backend_is_explicitでadapter正規化・graph構築・失敗境界の契約が回帰していないことを検証する。
    @patch('messenger.shutil.which', return_value=None)
    def test_missing_scip_backend_is_explicit(self, _which):
        result = scip_print_json('index.scip')
        self.assertFalse(result['ok'])
        self.assertEqual('backend_unavailable', result['status'])
        self.assertEqual('scip', result['backend'])


if __name__ == '__main__':
    unittest.main()
