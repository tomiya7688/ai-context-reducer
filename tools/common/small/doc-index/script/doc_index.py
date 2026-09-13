#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

IGNORE = {'.git', '.venv', 'venv', 'node_modules', 'bin', 'obj', 'build', 'dist', '__pycache__'}


def build_index(root: Path, max_documents: int, max_headings_per_document: int) -> dict[str, object]:
    documents = []
    documents_scanned = 0
    read_error_paths = []
    documents_truncated = False

    for p in root.rglob('*.md'):
        if any(part in IGNORE for part in p.parts):
            continue
        documents_scanned += 1
        try:
            text = p.read_text(encoding='utf-8', errors='replace')
        except OSError:
            read_error_paths.append(p.relative_to(root).as_posix())
            continue

        headings = []
        total_headings = 0
        for n, line in enumerate(text.splitlines(), 1):
            m = re.match(r'^(#{1,3})\s+(.+?)\s*$', line)
            if not m:
                continue
            total_headings += 1
            if max_headings_per_document == 0 or len(headings) < max_headings_per_document:
                headings.append({'line': n, 'level': len(m.group(1)), 'title': m.group(2)[:120]})
        if headings:
            documents.append({
                'path': p.relative_to(root).as_posix(),
                'heading_count': total_headings,
                'headings': headings,
                'headings_truncated': max_headings_per_document > 0 and total_headings > len(headings),
            })
            if max_documents > 0 and len(documents) >= max_documents:
                documents_truncated = True
                break

    return {
        'tool': 'doc-index',
        'status': 'ok',
        'project_root': str(root),
        'markdown_files_scanned': documents_scanned,
        'read_error_paths': read_error_paths,
        'documents': documents,
        'documents_truncated': documents_truncated,
    }


def main():
    ap = argparse.ArgumentParser(description='Build a compact Markdown heading index as self-describing JSON.')
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--max-documents', type=int, default=0, help='Optional output limit. 0 means unlimited.')
    ap.add_argument('--max-headings-per-document', type=int, default=60, help='Heading output limit per document. 0 means unlimited.')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        result = {'tool': 'doc-index', 'status': 'input_missing', 'project_root': str(root)}
    elif not root.is_dir():
        result = {'tool': 'doc-index', 'status': 'input_not_directory', 'project_root': str(root)}
    else:
        result = build_index(root, max(0, args.max_documents), max(0, args.max_headings_per_document))
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
