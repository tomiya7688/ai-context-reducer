from __future__ import annotations

import re

RULE_WORDS = ('must', 'must not', 'should', 'should not', 'required', 'recommended', '禁止', '必須', '推奨', 'してはならない', 'すること')


def policy_findings(lines: list[str]):
    heading = ''
    for number, line in enumerate(lines, 1):
        if re.match(r'^#{1,6}\s+', line):
            heading = line.strip('# ').strip()
        low = line.lower()
        if any(word in low for word in RULE_WORDS):
            yield number, heading or 'no-heading', line.strip()[:220]
