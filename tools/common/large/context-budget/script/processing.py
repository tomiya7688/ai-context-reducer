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


def summarize(rows: list[tuple[int, int, str]], top: int, mode: str, scanned: int, truncated: bool) -> str:
    rows.sort(reverse=True)
    total = sum(row[0] for row in rows)
    lines = [
        f'mode={mode}',
        f'estimated_total_tokens_if_all_candidates_read={total}',
        f'scanned_text_files={scanned}',
        f'truncated={str(truncated).lower()}',
        'largest_candidates:',
    ]
    suffix = '' if mode == 'accurate' else '~'
    for tokens, size, path in rows[:top]:
        lines.append(f'  {tokens:>8} tok{suffix}  {size:>10} bytes  {path}')
    if len(rows) > top:
        lines.append(f'  ... {len(rows) - top} more analyzed files')
    return '\n'.join(lines)
