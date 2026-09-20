import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "common" / "native" / "acr-toolbox"
FUNC_RE = re.compile(r"^(\s*)func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")


def has_japanese_comment(lines, index):
    """named function直前の連続comment blockに日本語があるか確認する。"""
    cursor = index - 1
    while cursor >= 0 and not lines[cursor].strip():
        cursor -= 1
    found_comment = False
    while cursor >= 0:
        text = lines[cursor].strip()
        if text.startswith("//") or text.startswith("/*") or text.startswith("*") or text.endswith("*/"):
            found_comment = True
            if JAPANESE_RE.search(text):
                return True
            cursor -= 1
            continue
        break
    return False and found_comment


class AcrToolboxJapaneseCommentTests(unittest.TestCase):
    def test_all_named_functions_have_japanese_comment(self):
        """全named function/methodが日本語commentを持つことを回帰検証する。"""
        missing = []
        for path in sorted(TARGET.glob("*.go")):
            lines = path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                match = FUNC_RE.match(line)
                if match and not has_japanese_comment(lines, index):
                    missing.append(f"{path.name}:{index + 1}:{match.group(2)}")
        self.assertEqual([], missing, "日本語comment不足:\n" + "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
