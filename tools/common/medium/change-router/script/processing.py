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
            if bool(row['is_test']):
                tests.append(path)
            elif bool(row['is_doc']):
                docs.append(path)

    limit = max(0, limit)
    returned_tests = tests[:limit] if limit > 0 else tests
    returned_docs = docs[:limit] if limit > 0 else docs
    return {
        'changed_file': rel,
        'candidate_tests': returned_tests,
        'candidate_tests_truncated': len(tests) > len(returned_tests),
        'candidate_docs': returned_docs,
        'candidate_docs_truncated': len(docs) > len(returned_docs),
    }
