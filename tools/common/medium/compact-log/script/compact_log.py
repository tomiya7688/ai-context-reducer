#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

PATTERN = re.compile(r'(error|failed|failure|fatal|exception|warning|warn|assert|traceback|ng\b)', re.I)


def compact_log(text: str, max_findings: int, tail: int) -> dict[str, object]:
    lines = text.splitlines()
    findings = [
        {'line': number, 'text': line[:240]}
        for number, line in enumerate(lines, 1)
        if PATTERN.search(line)
    ]
    tail_start = max(0, len(lines) - tail)
    return {
        'line_count': len(lines),
        'finding_count': len(findings),
        'findings': findings[:max_findings],
        'findings_truncated': len(findings) > max_findings,
        'tail': [
            {'line': number, 'text': line[:240]}
            for number, line in enumerate(lines[tail_start:], tail_start + 1)
        ],
    }


def main():
    parser = argparse.ArgumentParser(description='Reduce long validation logs to high-signal findings and a bounded tail.')
    parser.add_argument('file', nargs='?')
    parser.add_argument('--max-findings', type=int, default=80)
    parser.add_argument('--tail', type=int, default=20)
    args = parser.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            result = {'tool': 'compact-log', 'status': 'input_missing', 'input_file': str(path)}
        else:
            try:
                text = path.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                result = {'tool': 'compact-log', 'status': 'read_failed', 'input_file': str(path)}
            else:
                result = {'tool': 'compact-log', 'status': 'ok', 'input_file': str(path), **compact_log(text, args.max_findings, args.tail)}
    else:
        result = {'tool': 'compact-log', 'status': 'ok', 'input': 'stdin', **compact_log(sys.stdin.read(), args.max_findings, args.tail)}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
