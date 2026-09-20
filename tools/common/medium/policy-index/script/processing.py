from __future__ import annotations

import re

ENGLISH_RULE_TERMS = ('must not', 'should not', 'must', 'should', 'required', 'recommended')
JAPANESE_RULE_TERMS = ('禁止', '必須', '推奨', 'してはならない', 'すること')
ENGLISH_RULE_PATTERN = re.compile(
    r'\b(?:' + '|'.join(re.escape(term) for term in ENGLISH_RULE_TERMS) + r')\b',
    re.IGNORECASE,
)
HEADING_PATTERN = re.compile(r'^#{1,6}\s+')


# is_policy_line はroutingやfallback判断に使う条件を判定する。
def is_policy_line(line: str) -> bool:
    if ENGLISH_RULE_PATTERN.search(line):
        return True
    return any(term in line for term in JAPANESE_RULE_TERMS)


# policy_findings はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def policy_findings(lines: list[str]):
    heading = ''
    for number, line in enumerate(lines, 1):
        if HEADING_PATTERN.match(line):
            heading = line.lstrip('#').strip()
        if is_policy_line(line):
            yield number, heading or 'no-heading', line.strip()[:220]
