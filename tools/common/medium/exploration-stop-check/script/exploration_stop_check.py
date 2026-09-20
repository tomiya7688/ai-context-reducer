#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

CHECKS = {
    'goal': ('goal', '目的'),
    'required': ('required', 'requirement', '要件', '必須', '制約'),
    'acceptance': ('acceptance', '完了条件', '受け入れ', 'completion'),
    'deferred': ('deferred', 'out of scope', '非対象', '対象外'),
    'source': ('source', 'target file', '対象ファイル', '実装'),
    'tests': ('test', 'tests', '検証', 'validation'),
}
REQUIRED = ('goal', 'required', 'acceptance', 'source', 'tests')


# term_present はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def term_present(text: str, term: str) -> bool:
    if any(ord(char) > 127 for char in term):
        return term in text
    return re.search(rf'(?<![a-z0-9_]){re.escape(term)}(?![a-z0-9_])', text) is not None


# evaluate はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def evaluate(text: str) -> dict[str, object]:
    lowered = text.lower()
    checks = {key: any(term_present(lowered, word) for word in words) for key, words in CHECKS.items()}
    missing = [key for key in REQUIRED if not checks[key]]
    return {
        'checks': checks,
        'required_checks': list(REQUIRED),
        'missing_required_checks': missing,
        'stop_broad_exploration': not missing,
    }


# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    parser = argparse.ArgumentParser(description='Check whether task context is sufficient to stop broad exploration.')
    parser.add_argument('file')
    args = parser.parse_args()
    path = Path(args.file)

    if not path.exists():
        result = {
            'tool': 'exploration-stop-check',
            'status': 'input_missing',
            'input_file': str(path),
        }
    elif not path.is_file():
        result = {
            'tool': 'exploration-stop-check',
            'status': 'input_not_file',
            'input_file': str(path),
        }
    else:
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            result = {
                'tool': 'exploration-stop-check',
                'status': 'read_failed',
                'input_file': str(path),
            }
        else:
            result = {
                'tool': 'exploration-stop-check',
                'status': 'ok',
                'input_file': str(path),
                **evaluate(text),
            }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
