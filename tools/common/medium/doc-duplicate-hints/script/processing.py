from __future__ import annotations

import hashlib
import re
from collections import defaultdict


def normalize(line: str) -> str:
    line = re.sub(r'\s+', ' ', line.strip().lower())
    return re.sub(r'[`*_>#-]', '', line).strip()


def collect_duplicates(documents: list[tuple[str, list[str]]], min_chars: int):
    seen = defaultdict(list)
    for path, lines in documents:
        for number, line in enumerate(lines, 1):
            norm = normalize(line)
            if len(norm) < min_chars:
                continue
            key = hashlib.sha1(norm.encode()).hexdigest()
            seen[key].append((path, number, line.strip()))

    groups = []
    for items in seen.values():
        if len({item[0] for item in items}) >= 2:
            groups.append(items)
    return groups
