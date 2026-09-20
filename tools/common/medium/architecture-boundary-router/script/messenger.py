from __future__ import annotations

import json


# load_profile は必要な入力だけを読み込み、後段が扱いやすい形へ整える。
def load_profile(path: str) -> dict[str, object]:
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)
