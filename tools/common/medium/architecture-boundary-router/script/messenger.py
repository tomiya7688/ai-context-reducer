from __future__ import annotations

import json


def load_profile(path: str) -> dict[str, object]:
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)
