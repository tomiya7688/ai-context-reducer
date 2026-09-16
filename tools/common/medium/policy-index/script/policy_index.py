#!/usr/bin/env python3
import argparse
import json
import sys

from messenger import discover_policy_files, read_lines
from processing import policy_findings


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description='Index likely policy/rule lines as compact self-describing JSON.')
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--max-findings', type=int, default=120, help='Maximum findings returned. 0 means unlimited.')
    args = parser.parse_args()

    files, missing_inputs, unsupported_inputs, walk_error_count = discover_policy_files(args.paths)
    all_findings = []
    read_errors = []
    scanned_policy_files = 0

    for path in files:
        lines = read_lines(path)
        if lines is None:
            read_errors.append(str(path))
            continue
        scanned_policy_files += 1
        for number, heading, text in policy_findings(lines):
            all_findings.append({
                'path': str(path),
                'line': number,
                'heading': heading,
                'rule_text': text,
            })

    limit = max(0, args.max_findings)
    findings = all_findings if limit == 0 else all_findings[:limit]
    truncated = len(findings) < len(all_findings)

    warnings = bool(missing_inputs or unsupported_inputs or read_errors or walk_error_count)
    if not files and missing_inputs:
        status = 'input_unavailable'
    elif not files:
        status = 'no_policy_documents'
    elif warnings:
        status = 'partial'
    else:
        status = 'ok'

    result = {
        'tool': 'policy-index',
        'status': status,
        'discovered_policy_files': len(files),
        'scanned_policy_files': scanned_policy_files,
        'finding_count_total': len(all_findings),
        'findings': findings,
        'findings_truncated': truncated,
        'missing_inputs': missing_inputs,
        'unsupported_inputs': unsupported_inputs,
        'read_error_paths': read_errors,
        'walk_error_count': walk_error_count,
    }
    emit(result)
    return 2 if status == 'input_unavailable' else 0


if __name__ == '__main__':
    sys.exit(main())
