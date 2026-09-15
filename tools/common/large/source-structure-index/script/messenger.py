from __future__ import annotations

import json
from pathlib import Path


def load_json(path: str) -> object:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path: str, payload: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
