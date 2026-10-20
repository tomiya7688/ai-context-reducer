import tempfile
import unittest
from pathlib import Path
from src.settings import SettingsLoadError, load_settings

class SettingsTests(unittest.TestCase):
    def test_invalid_settings_reports_decode_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text("{bad", encoding="utf-8")
            with self.assertRaises(SettingsLoadError):
                load_settings(path)

if __name__ == "__main__":
    unittest.main()
