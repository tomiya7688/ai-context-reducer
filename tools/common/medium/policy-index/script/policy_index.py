#!/usr/bin/env python3
import argparse
import json

from messenger import discover_policy_files, read_lines
from processing import policy_findings


def main():
    parser = argparse.ArgumentParser(description='Index likely policy/rule lines as compact self-describing JSON.')
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--max-findings', type=int, default=120)
    args = parser.parse_args()

    files, missing_inputs = discover_policy_files(args.paths)
    findings = []
    read_errors = []
    truncated = False

    for path in files:
        lines = read_lines(path)
        if lines is None:
            read_errors.append(str(path))
            continue
        for number, heading, text in policy_findings(lines):
            if len(findings) >= args.max_findings:
                truncated = True
                break
            findings.append({
                'path': str(path),
                'line': number,
                'heading': heading,
                'rule_text': text,
            })
        if truncated:
            break

    status = 'ok'
    if missing_inputs or read_errors:
        status = 'partial'
    if not files and missing_inputs:
        status = 'input_unavailable'

    result = {
        'tool': 'policy-index',
        'status': status,
        'scanned_policy_files': len(files),
        'findings': findings,
        'findings_truncated': truncated,
        'missing_inputs': missing_inputs,
        'read_error_paths': read_errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
