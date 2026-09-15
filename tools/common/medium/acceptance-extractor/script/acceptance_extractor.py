#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

HEADINGS = {
    'goal': ('goal', '目的', '概要'),
    'required': ('required', 'requirements', '要件', '必須', '制約'),
    'acceptance': ('acceptance', '受け入れ', '完了条件', 'completion', 'done'),
    'deferred': ('deferred', 'out of scope', '非対象', '対象外', '今後', 'future'),
}


def term_present(text: str, term: str) -> bool:
    if any(ord(char) > 127 for char in term):
        return term in text
    return re.search(rf'(?<![a-z0-9_]){re.escape(term)}(?![a-z0-9_])', text) is not None


def section(lines: list[str], start: int, limit: int) -> tuple[list[str], bool]:
    limit = max(0, limit)
    out = []
    for i in range(start + 1, len(lines)):
        if re.match(r'^#{1,6}\s+', lines[i]):
            break
        if lines[i].strip():
            out.append(lines[i].rstrip())
    return out[:limit], len(out) > limit


def extract_sections(lines: list[str], limit: int) -> tuple[dict[str, list[str]], dict[str, bool]]:
    sections = {key: [] for key in HEADINGS}
    truncated = {key: False for key in HEADINGS}
    for i, line in enumerate(lines):
        match = re.match(r'^#{1,6}\s+(.+)$', line.strip())
        if not match:
            continue
        title = match.group(1).lower()
        for key, words in HEADINGS.items():
            if any(term_present(title, word) for word in words):
                values, was_truncated = section(lines, i, limit)
                sections[key].extend(values)
                truncated[key] = truncated[key] or was_truncated
    return sections, truncated


def main():
    parser = argparse.ArgumentParser(description='Extract Goal/Required/Acceptance/Deferred sections from markdown as self-describing JSON.')
    parser.add_argument('file')
    parser.add_argument('--max-lines-per-section', type=int, default=40)
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(json.dumps({
            'tool': 'acceptance-extractor',
            'status': 'input_missing',
            'input_file': str(path),
        }, ensure_ascii=False, indent=2))
        return
    if not path.is_file():
        print(json.dumps({
            'tool': 'acceptance-extractor',
            'status': 'input_not_file',
            'input_file': str(path),
        }, ensure_ascii=False, indent=2))
        return

    try:
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError:
        print(json.dumps({
            'tool': 'acceptance-extractor',
            'status': 'read_failed',
            'input_file': str(path),
        }, ensure_ascii=False, indent=2))
        return

    sections, truncated = extract_sections(lines, max(0, args.max_lines_per_section))
    print(json.dumps({
        'tool': 'acceptance-extractor',
        'status': 'ok',
        'input_file': str(path),
        'sections': sections,
        'section_truncated': truncated,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
