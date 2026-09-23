#!/usr/bin/env python3
import sys
from pathlib import Path

# 旧tool pathを維持しつつ、実装本体は標準script/配置へ委譲する互換entrypoint。
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from script.affected_tests import *  # noqa: F401,F403,E402


if __name__ == '__main__':
    raise SystemExit(main())
