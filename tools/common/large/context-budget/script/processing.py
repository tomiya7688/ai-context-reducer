from __future__ import annotations

from pathlib import Path

from messenger import file_size, read_text


def estimate_fast(path: Path):
    size = file_size(path)
    if size is None:
        return None
    return max(1, size // 4), size


def estimate_accurate(path: Path):
    text = read_text(path)
    if text is None:
        return None
    size = len(text.encode('utf-8', errors='ignore'))
    return max(1, len(text) // 4), size


def summarize(rows: list[tuple[int, int, str]], top: int, mode: str, scanned: int, truncated: bool) -> dict[str, object]:
    rows.sort(reverse=True)
    total = sum(row[0] for row in rows)
    return {
        'tool': 'context-budget',
        'status': 'ok',
        'mode': mode,
        'estimated_total_tokens_if_all_candidates_read': total,
        'scanned_text_files': scanned,
        'scan_truncated': truncated,
        'largest_context_candidates': [
            {
                'path': path,
                'estimated_tokens': tokens,
                'token_estimate_is_approximate': mode != 'accurate',
                'bytes': size,
            }
            for tokens, size, path in rows[:top]
        ],
        'largest_context_candidates_truncated': len(rows) > top,
    }
