from __future__ import annotations

import hashlib
import re
from collections import defaultdict


def normalize(line: str) -> str:
    line = re.sub(r'\s+', ' ', line.strip().lower())
    return re.sub(r'[`*_>#-]', '', line).strip()


def collect_duplicates(documents: list[tuple[str, list[str]]], min_chars: int):
    min_chars = max(0, min_chars)
    seen = defaultdict(list)
    representative = {}
    for path, lines in sorted(documents, key=lambda item: item[0]):
        for number, line in enumerate(lines, 1):
            norm = normalize(line)
            if len(norm) < min_chars:
                continue
            key = hashlib.sha1(norm.encode()).hexdigest()
            representative.setdefault(key, line.strip())
            seen[key].append({'path': path, 'line': number})

    groups = []
    for key, occurrences in seen.items():
        if len({item['path'] for item in occurrences}) < 2:
            continue
        occurrences.sort(key=lambda item: (item['path'], item['line']))
        groups.append({
            'repeated_text': representative[key][:180],
            'occurrences': occurrences,
        })
    groups.sort(key=lambda group: (-len(group['occurrences']), group['repeated_text'].lower()))
    return groups
