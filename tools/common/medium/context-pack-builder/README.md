# context-pack-builder

Context Pack の生成toolです。

## Development routing

- CLI変更: `script/context_pack_builder.py`
- Git状態取得の変更: Git boundary helper
- Context Pack本文・項目変更: rendering / processing helper
- 全体flow変更: orchestration helper

分割は、ai-context-reducer自身の Task Routing / Responsibility Map / Targeted Validation をtool開発へ適用するために行います。小変更で無関係な責務を読ませないことを優先します。
