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


def summarize(
    rows: list[tuple[int, int, str]],
    top: int,
    mode: str,
    scanned: int,
    truncated: bool,
    estimation_error_count: int = 0,
) -> dict[str, object]:
    rows.sort(reverse=True)
    total = sum(row[0] for row in rows)
    estimator = {
        'unit': 'estimated_tokens',
        'approximate': True,
        'formula': 'file_size_bytes_div_4' if mode == 'fast' else 'decoded_text_characters_div_4',
        'reads_file_contents': mode == 'accurate',
        'note': 'This is a routing estimate, not tokenizer-exact token counting.',
    }
    return {
        'tool': 'context-budget',
        'status': 'ok_with_warnings' if estimation_error_count else 'ok',
        'mode': mode,
        'token_estimate': estimator,
        'estimated_total_tokens_if_all_candidates_read': total,
        'scanned_text_files': scanned,
        'estimation_error_count': estimation_error_count,
        'scan_truncated': truncated,
        'largest_context_candidates': [
            {
                'path': path,
                'estimated_tokens': tokens,
                'bytes': size,
            }
            for tokens, size, path in rows[:top]
        ],
        'largest_context_candidates_truncated': len(rows) > top,
    }
