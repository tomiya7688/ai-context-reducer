from __future__ import annotations

from pathlib import Path


def normalized_stem(rel: str) -> str:
    stem = Path(rel).stem.lower()
    if stem.startswith('test_'):
        stem = stem[5:]
    if stem.endswith('_test'):
        stem = stem[:-5]
    return stem


def route_candidates(rel: str, index: list[dict[str, object]], limit: int) -> dict[str, object]:
    stem = normalized_stem(rel)
    tests: list[str] = []
    docs: list[str] = []

    if stem:
        for row in index:
            name = str(row['name'])
            if stem not in name:
                continue
            path = str(row['path'])
            if bool(row['is_test']) and len(tests) < limit:
                tests.append(path)
            elif bool(row['is_doc']) and len(docs) < limit:
                docs.append(path)
            if len(tests) >= limit and len(docs) >= limit:
                break

    return {
        'changed_file': rel,
        'candidate_tests': tests,
        'candidate_docs': docs,
    }
